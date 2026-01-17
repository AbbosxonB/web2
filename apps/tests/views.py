from rest_framework import viewsets, permissions, status, decorators, filters
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
import openpyxl

from .models import Test, Question
from .serializers import TestSerializer, QuestionSerializer
from .excel_import import import_questions_from_excel
from apps.results.models import TestResult, StudentAnswer

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'subject__name']

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        
        # Unauthenticated users shouldn't see anything ideally, but DRF handles 401.
        if not user.is_authenticated:
            return Test.objects.none()

        if user.role == 'student':
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

    @decorators.action(detail=True, methods=['get'], url_path='start')

    def start_test(self, request, pk=None):
        test = self.get_object()
        student = request.user.student_profile
        
        # Check if already taken
        # Check if already taken and NOT allowed to retake
        active_results = TestResult.objects.filter(student=student, test=test, can_retake=False)
        if active_results.exists():
             return Response({'error': 'Siz bu testni topshirgansiz.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check start/end dates
        from django.utils import timezone
        now = timezone.now()
        
        if now < test.start_date:
            return Response({'error': f"Test hali boshlanmagan. Boshlanish vaqti: {test.start_date.strftime('%d.%m.%Y %H:%M')}"}, status=status.HTTP_400_BAD_REQUEST)
            
        if now > test.end_date:
            return Response({'error': "Test vaqti tugagan."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Randomize unique questions
        all_questions = list(test.questions.all())
        # Shuffle regardless of count to ensure randomness if count == 25, 
        # and slice if > 25.
        import random
        random.shuffle(all_questions)
        selected_questions = all_questions[:25]
        
        # Serialize
        test_data = TestSerializer(test).data
        test_data['questions'] = QuestionSerializer(selected_questions, many=True).data
        
        return Response(test_data)

    @decorators.action(detail=True, methods=['post'], url_path='submit')
    def submit_test(self, request, pk=None):
        test = self.get_object()
        student = request.user.student_profile
        
        # Check if already taken
        # Allow retakes? User didn't specify. Assuming single attempt for now as per original logic.
        if TestResult.objects.filter(student=student, test=test, can_retake=False).exists():
             return Response({'error': 'Siz bu testni topshirgansiz.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If retake allowed, we perhaps should mark previous ones as retaken or just create new one.
        # Creating new one is fine as per model structure (no unique constraint).
        # We might want to set can_retake=False on older ones to be sure, or just rely on 'latest' logic elsewhere.
        # For simple logic, we just proceed to create NEW result.
        pass

        answers_data = request.data.get('answers', {})
        score = 0
        MAX_SCORE_FIXED = 50
        PASSING_SCORE_FIXED = 30
        POINTS_PER_QUESTION = 2
        
        # Create Result Placeholder
        result = TestResult.objects.create(
            student=student,
            test=test,
            score=0,
            max_score=MAX_SCORE_FIXED, 
            percentage=0,
            status='failed',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        # Iterate over submitted answers to respect the "random 25" subset the student saw.
        # We assume the frontend sends back answers for the questions it rendered.
        # Security Note: Ideally we track the session, but for now we trust the question IDs sent.
        # We can also iterate ALL questions and check if they are in answers, but that breaks if test > 25 questions.
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
        
        # Capping score just in case logic weirdness or more than 25 answers sent (hacker check).
        if score > MAX_SCORE_FIXED: score = MAX_SCORE_FIXED
        
        # Update Result
        result.score = score
        result.max_score = MAX_SCORE_FIXED
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
    print(f"DEBUG: take_test_view called with id {test_id}")
    return render(request, 'tests/take_test.html', {'test_id': test_id})

def test_list_view(request):
    return render(request, 'crud_list.html', {'page': 'tests'})

def edit_test_view(request, test_id):
    return render(request, 'tests/edit_test.html', {'test_id': test_id})
