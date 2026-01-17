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
        return TestResult.objects.all().select_related('student', 'test', 'student__group')

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
        headers = ["Talaba", "Guruh", "Test", "Ball", "Maks. Ball", "Foiz", "Holat", "Sana"]
        ws.append(headers)

        for result in queryset:
            student_name = result.student.full_name if result.student else "Noma'lum"
            group_name = result.student.group.name if (result.student and result.student.group) else "-"
            test_title = result.test.title if result.test else "-"
            
            ws.append([
                student_name,
                group_name,
                test_title,
                result.score,
                result.max_score,
                f"{result.percentage:.1f}%",
                result.status,
                result.completed_at.strftime("%d.%m.%Y %H:%M") if result.completed_at else "-"
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=natijalar.xlsx'
        wb.save(response)
        return response

from django.shortcuts import render
def result_list_view(request):
    return render(request, 'crud_list.html', {'page': 'results'})
