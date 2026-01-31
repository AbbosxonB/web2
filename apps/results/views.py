from rest_framework import viewsets, permissions, filters, status, decorators, pagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import TestResult
from .serializers import TestResultSerializer

class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'test', 'student__group']
    search_fields = ['student__full_name', 'test__title', 'student__group__name']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            # Students only see their own results
            return TestResult.objects.filter(student__user=user)
        
        queryset = TestResult.objects.all().select_related('student', 'test', 'student__group')

        # Date Filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(completed_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(completed_at__date__lte=end_date)
            
        # Student Filters
        course = self.request.query_params.get('course')
        edu_form = self.request.query_params.get('education_form')
        direction = self.request.query_params.get('direction')
        
        if course:
            queryset = queryset.filter(student__course=course)
        if edu_form:
            queryset = queryset.filter(student__education_form=edu_form)
        if direction:
            queryset = queryset.filter(student__direction__icontains=direction)
            
        return queryset

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Natijani o'chirish uchun faqat Admin huquqi talab qilinadi.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def allow_retake(self, request, pk=None):
        user = request.user
        if user.role not in ['admin', 'dean']:
             return Response({'error': 'Huquq yo\'q'}, status=status.HTTP_403_FORBIDDEN)
        
        result = self.get_object()
        result.can_retake = True
        result.retake_granted_by = user
        result.save()
        return Response({'status': 'retake_granted'})

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        user = request.user
        if user.role not in ['admin', 'dean']:
            return Response({'error': 'Huquq yo\'q'}, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'error': 'Hech narsa tanlanmadi'}, status=status.HTTP_400_BAD_REQUEST)
            
        queryset = TestResult.objects.filter(id__in=ids)
        
        if action == 'delete':
            # Check delete permission if needed, but admin/dean is already checked
            queryset.delete()
            return Response({'status': 'deleted', 'count': len(ids)})
            
        elif action == 'retake':
            queryset.update(can_retake=True, retake_granted_by=user)
            return Response({'status': 'retake_granted', 'count': len(ids)})
            
        return Response({'error': 'Noto\'g\'ri amal'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        import openpyxl
        from django.http import HttpResponse

        user = request.user
        if user.role not in ['admin', 'dean']:
             return Response({'error': 'Huquq yo\'q'}, status=status.HTTP_403_FORBIDDEN)

        # Apply filters
        queryset = self.filter_queryset(self.get_queryset())

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Natijalar"

        # Headers
        headers = ["ID", "Talaba", "Guruh", "Test", "Ball", "Maks. Ball", "Foiz", "Holat", "Tugagan vaqti", "Sarflangan vaqt", "Sana"]
        ws.append(headers)

        from django.utils import timezone
        
        for result in queryset:
            student_name = result.student.full_name if result.student else "Noma'lum"
            group_name = result.student.group.name if (result.student and result.student.group) else "-"
            test_title = result.test.title if result.test else "-"
            
            # Calculate duration
            duration_str = "-"
            if result.completed_at and result.started_at:
                diff = result.completed_at - result.started_at
                total_seconds = int(diff.total_seconds())
                if total_seconds < 60:
                    duration_str = f"{total_seconds} sek"
                else:
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    duration_str = f"{minutes} min {seconds} sek"

            # Localize times
            completed_str = "-"
            if result.completed_at:
                completed_str = timezone.localtime(result.completed_at).strftime("%d.%m.%Y %H:%M")

            started_str = "-"
            if result.started_at:
                started_str = timezone.localtime(result.started_at).strftime("%d.%m.%Y %H:%M")

            ws.append([
                result.id,
                student_name,
                group_name,
                test_title,
                result.score,
                result.max_score,
                f"{result.percentage:.1f}%",
                result.status,
                completed_str,
                duration_str,
                started_str
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=natijalar.xlsx'
        wb.save(response)
        return response

from django.shortcuts import render
def result_list_view(request):
    return render(request, 'crud_list.html', {'page': 'results'})
