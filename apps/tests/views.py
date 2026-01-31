from rest_framework import viewsets, permissions, status, decorators, filters, pagination
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
import openpyxl

from .models import Test, Question
from .serializers import TestSerializer, QuestionSerializer
from .excel_import import import_questions_from_excel
from apps.results.models import TestResult, StudentAnswer

class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    from apps.accounts.granular_permissions import GranularPermission

    class StudentTestPermission(GranularPermission):
        def has_permission(self, request, view):
            # Allow students to view list, details, and perform taking-test actions
            if request.user.is_authenticated and request.user.role == 'student':
                if view.action in ['list', 'retrieve', 'start_test', 'submit_test', 'snapshot']:
                    return True
                return False
            # For others, fall back to standard Granular Permission (ModuleAccess check)
            return super().has_permission(request, view)

    permission_classes = [permissions.IsAuthenticated, StudentTestPermission]
    module_name = 'tests'
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'subject__name']

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        
        # Unauthenticated users shouldn't see anything ideally, but DRF handles 401.
        if not user.is_authenticated:
            return Test.objects.none()

        if user.role == 'student':
            # Check if profile exists to avoid 500 error if data is inconsistent
            if not hasattr(user, 'student_profile'):
                return Test.objects.none()
                
            # Active tests assigned to their group
            # Use 'active' status filter? Original code didn't filter by status here, only in student specific logic maybe?
            # User requirement says "assigned tests". Let's stick to group assignment.
            # Adding status='active' might prevent seeing past results if we use this for results? 
            # But this is TestViewSet, primarily for listing available tests to take.
            return Test.objects.filter(groups=user.student_profile.group, status='active')
            
        if user.role == 'teacher':
             # Created by them OR Subject assigned to them
             return Test.objects.filter(Q(created_by=user) | Q(subject__teacher=user)).distinct()
             
        return Test.objects.all()

    @decorators.action(detail=True, methods=['post'], url_path='update-groups')
    def update_groups(self, request, pk=None):
        test = self.get_object()
        group_ids = request.data.get('group_ids', [])
        
        # Validate groups
        from apps.groups.models import Group
        groups = list(Group.objects.filter(id__in=group_ids))
        
        # Current assignments
        from apps.tests.models import TestAssignment
        current_assignments = TestAssignment.objects.filter(test=test)
        current_group_ids = set(current_assignments.values_list('group_id', flat=True))
        new_group_ids = set(g.id for g in groups)
        
        # To Delete (in current but not in new)
        to_delete = current_group_ids - new_group_ids
        TestAssignment.objects.filter(test=test, group_id__in=to_delete).delete()
        
        # To Create (in new but not in current)
        to_create = new_group_ids - current_group_ids
        new_assignments = []
        for gid in to_create:
            new_assignments.append(TestAssignment(test=test, group_id=gid))
        TestAssignment.objects.bulk_create(new_assignments)
        
        return Response({
            'status': 'success',
            'message': f"Guruhlar yangilandi. {len(to_create)} ta qo'shildi, {len(to_delete)} ta o'chirildi."
        })

    @decorators.action(detail=True, methods=['post'], url_path='assign-group')
    def assign_group(self, request, pk=None):
        test = self.get_object()
        group_ids = request.data.get('group_ids', [])
        
        # Support single ID legacy/fallback
        single_id = request.data.get('group_id')
        if single_id:
            group_ids.append(single_id)
            
        if not group_ids:
            return Response({'error': 'Guruhlar tanlanmagan'}, status=status.HTTP_400_BAD_REQUEST)
            
        from apps.groups.models import Group
        from apps.tests.models import TestAssignment

        try:
            groups = Group.objects.filter(id__in=group_ids)
            if not groups.exists():
                 return Response({'error': 'Tizimda bunday guruhlar mavjud emas'}, status=status.HTTP_404_NOT_FOUND)

            assigned_count = 0
            for group in groups:
                obj, created = TestAssignment.objects.get_or_create(test=test, group=group)
                if created:
                    assigned_count += 1
            
            return Response({
                'status': 'success', 
                'message': f"Test {assigned_count} ta yangi guruhga biriktirildi. Jami: {groups.count()} ta guruh tanlangan."
            })
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['post'], url_path='import-questions')
    def import_questions(self, request, pk=None):
        test = self.get_object()
        file = request.FILES.get('file')
        
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            questions_data = import_questions_from_excel(file)
            questions = []
            for q_data in questions_data:
                questions.append(Question(test=test, **q_data))
            
            Question.objects.bulk_create(questions)
            return Response({'status': 'success', 'count': len(questions)})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['post'], url_path='snapshot')
    def snapshot(self, request, pk=None):
        test = self.get_object()
        student = request.user.student_profile
        image = request.FILES.get('image')
        
        if not image:
            return Response({'error': 'No image provided'}, status=400)
            
        from .models import TestSnapshot
        TestSnapshot.objects.create(test=test, student=student, image=image)
        
        # Update user last_activity for "Online" status
        request.user.last_activity = timezone.now()
        request.user.save()
        
        return Response({'status': 'saved'})

    @decorators.action(detail=True, methods=['get'], url_path='start')

    def start_test(self, request, pk=None):
        print(f"DEBUG: start_test called for test {pk} by user {request.user}")
        test = self.get_object()
        try:
            student = request.user.student_profile
        except:
             print("DEBUG: User has no student profile")
             return Response({'error': 'Talaba profili topilmadi'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already taken
        # Check if already taken and NOT allowed to retake
        # Allow entry if status is 'in_progress' (resume)
        active_results = TestResult.objects.filter(student=student, test=test, can_retake=False).exclude(status='in_progress')
        if active_results.exists():
             print(f"DEBUG: Active results exist: {active_results}")
             return Response({'error': 'Siz bu testni topshirgansiz.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check mobile access
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_mobile = 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent
        
        if is_mobile and not test.allow_mobile_access:
             print(f"DEBUG: Mobile access denied for test {test.id}")
             return Response({'error': 'Ushbu testni telefonda ishlashga ruxsat berilmagan.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check start/end dates
        from django.utils import timezone
        now = timezone.now()
        
        if now < test.start_date:
            print(f"DEBUG: Early start. Now: {now}, Start: {test.start_date}")
            return Response({'error': f"Test hali boshlanmagan. Boshlanish vaqti: {test.start_date.strftime('%d.%m.%Y %H:%M')}"}, status=status.HTTP_400_BAD_REQUEST)
            
        if now > test.end_date:
            print(f"DEBUG: Late start. Now: {now}, End: {test.end_date}")
            return Response({'error': "Test vaqti tugagan."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize or Get In-Progress Result
        # We need to distinguish between a new attempt and a resume (if we support resume)
        # For now, if there is an in-progress test, we strictly assume we continue it or restart it? 
        # User requirement implies simplistic flow. 
        # Let's create a result if no active one exists.
        
        result, created = TestResult.objects.get_or_create(
            student=student,
            test=test,
            status='in_progress',
            defaults={
                'started_at': timezone.now(),
                'score': 0,
                'max_score': 0,
                'percentage': 0,
                'can_retake': False
            }
        )
        
        # If found existing 'in_progress', we keep it (resume logic implicitly)
        # But we must ensure we don't overwrite 'started_at' if it exists.
        
        # Randomize unique questions
        all_questions = list(test.questions.all())
        import random
        random.shuffle(all_questions)
        selected_questions = all_questions[:25]
        
        # Serialize
        test_data = TestSerializer(test).data
        test_data['questions'] = QuestionSerializer(selected_questions, many=True).data

        # Camera Logic
        camera_required = False
        mode = student.camera_mode
        
        if mode == 'required':
            camera_required = True
        elif mode == 'not_required':
            camera_required = False
        else: # default
            from apps.monitoring.models import GlobalSetting
            val = GlobalSetting.get_value('camera_required_globally')
            camera_required = (val == 'true')
            
        test_data['is_camera_required'] = camera_required
        
        return Response(test_data)

    @decorators.action(detail=True, methods=['post'], url_path='submit')
    def submit_test(self, request, pk=None):
        test = self.get_object()
        student = request.user.student_profile
        
        # Find the active session
        try:
            result = TestResult.objects.get(student=student, test=test, status='in_progress')
        except TestResult.DoesNotExist:
             # Fallback: If no in_progress found (maybe legacy or error), check if already passed?
             # Or just return error.
             # If student hacked request without start_test?
             # Let's clean up: If they have a completed test, say done.
             if TestResult.objects.filter(student=student, test=test).exclude(status='in_progress').exists():
                  return Response({'error': 'Siz bu testni topshirgansiz.'}, status=status.HTTP_400_BAD_REQUEST)
             
             # If never started? Create new? 
             # Better to enforce start_test.
             return Response({'error': 'Test boshlanmagan. Iltimos qaytadan urining.'}, status=400)

        answers_data = request.data.get('answers', {})
        score = 0
        MAX_SCORE_FIXED = 50
        POINTS_PER_QUESTION = 2
        
        # Update existing result
        result.completed_at = timezone.now()
        
        student_answers = []
        
        for q_id, selected_key in answers_data.items():
            try:
                question = Question.objects.get(id=q_id, test=test)
            except Question.DoesNotExist:
                continue

            is_correct = False
            if selected_key == question.correct_answer:
                score += POINTS_PER_QUESTION
                is_correct = True
            
            student_answers.append(StudentAnswer(
                test_result=result,
                question=question,
                selected_answer=selected_key,
                is_correct=is_correct
            ))
            
        StudentAnswer.objects.bulk_create(student_answers)
        
        if score > MAX_SCORE_FIXED: score = MAX_SCORE_FIXED
        
        percentage = (score / MAX_SCORE_FIXED) * 100
        status_val = 'passed' if score >= test.passing_score else 'failed'
        
        result.score = score
        result.max_score = MAX_SCORE_FIXED
        result.percentage = percentage
        result.status = status_val
        result.save()
        
        return Response({
            'status': status_val,
            'score': score,
            'percentage': percentage,
            'max_score': MAX_SCORE_FIXED
        })
        result.percentage = round((score / MAX_SCORE_FIXED) * 100)
        is_passed = score >= PASSING_SCORE_FIXED
        result.status = 'passed' if is_passed else 'failed'
        result.save()
        
        # Custom Message
        message = "Tabriklaymiz, siz testdan o'tdingiz!" if is_passed else "Afsuski, siz testdan o'ta olmadingiz."
        
        return Response({
            'status': 'success',
            'score': score,
            'max_score': MAX_SCORE_FIXED,
            'percentage': result.percentage,
            'passed': is_passed,
            'message': message
        })

    @decorators.action(detail=False, methods=['get'], url_path='sample-questions')
    def download_sample(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Namuna"
        
        # Headers
        headers = ['Savol Matni', 'Variant A', 'Variant B', 'Variant C', 'Variant D', 'To\'g\'ri Javob (A/B/C/D)']
        ws.append(headers)
        
        # Sample Data
        sample_data = [
            ['Python tili qachon yaratilgan?', '1989', '1991', '2000', '1995', 'B'],
            ['Django nima?', 'Web framework', 'Database', 'OS', 'Browser', 'A'],
        ]
        
        for row in sample_data:
            ws.append(row)
            
        # Column width adjustment
        for col in range(1, 7):
            ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=namuna_savollar.xlsx'
        
        wb.save(response)
        return response



class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Question.objects.all()
        test_id = self.request.query_params.get('test')
        if test_id:
            queryset = queryset.filter(test_id=test_id)
        return queryset

def take_test_view(request, test_id):
    return render(request, 'tests/take_test.html', {'test_id': test_id})

def test_list_view(request):
    return render(request, 'crud_list.html', {'page': 'tests'})

def edit_test_view(request, test_id):
    return render(request, 'tests/edit_test.html', {'test_id': test_id})
