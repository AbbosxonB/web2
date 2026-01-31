from rest_framework import viewsets, permissions, filters, decorators, pagination
from rest_framework.response import Response
from .models import Student
from .serializers import StudentSerializer

class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    from apps.accounts.granular_permissions import GranularPermission
    # permission_classes = [permissions.AllowAny]
    permission_classes = [permissions.IsAuthenticated, GranularPermission]
    module_name = 'students'
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'student_id']
    ordering_fields = ['full_name']
    ordering = ['full_name']

    def get_queryset(self):
        # print(f"DEBUG: Query Params: {self.request.query_params}")
        queryset = Student.objects.all()
        group = self.request.query_params.get('group')
        direction = self.request.query_params.get('direction')
        course = self.request.query_params.get('course')
        education_form = self.request.query_params.get('education_form')

        if group:
            queryset = queryset.filter(group_id=group)
        if direction:
            queryset = queryset.filter(direction__icontains=direction)
        if course:
            queryset = queryset.filter(course=course)
        if education_form:
            queryset = queryset.filter(education_form__iexact=education_form)
            
        return queryset

    def update(self, request, *args, **kwargs):
        # Custom update to handle password or specific logic if needed, 
        # but mostly relying on serializer. 
        # Removing debug logging.
        return super().update(request, *args, **kwargs)

    @decorators.action(detail=False, methods=['post'])
    def bulk_action(self, request):
        user = request.user
        if user.role != 'admin' and (not user.permissions or not any(p.module == 'students' and p.can_update for p in user.permissions)):
             return Response({'error': 'Huquq yo\'q'}, status=403)
        
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'error': 'Hech narsa tanlanmadi'}, status=400)
            
        queryset = Student.objects.filter(id__in=ids)
        
        if action == 'delete':
             if user.role != 'admin' and (not user.permissions or not any(p.module == 'students' and p.can_delete for p in user.permissions)):
                 return Response({'error': 'O\'chirish uchun huquq yo\'q'}, status=403)
             queryset.delete()
             return Response({'status': 'deleted', 'count': len(ids)})
             
        elif action == 'activate':
            queryset.update(is_system_active=True)
            return Response({'status': 'activated', 'count': len(ids)})
            
        elif action == 'deactivate':
            queryset.update(is_system_active=False)
            return Response({'status': 'deactivated', 'count': len(ids)})
            
        return Response({'error': 'Noto\'g\'ri amal'}, status=400)

    @decorators.action(detail=False, methods=['post'], url_path='import')
    def import_students(self, request):
        file = request.FILES.get('file')
        if not file: return Response({'error': 'Fayl tanlanmadi'}, status=400)
        
        try:
            from .excel_import import import_students_from_excel
            count = import_students_from_excel(file)
            return Response({'status': 'success', 'count': count})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=400)

    @decorators.action(detail=False, methods=['get'], url_path='sample')
    def download_sample(self, request):
        import openpyxl
        from django.http import HttpResponse

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Namuna"
        
        # Headers
        headers = ['F.I.SH', 'Talaba ID', 'Guruh', 'Kurs', 'Yo\'nalish', 'Ta\'lim Shakli', 'Telefon', 'Email', 'Login', 'Parol']
        ws.append(headers)
        
        # Example Row
        ws.append(['Aliyev Vali', '392201101', '210-21', 1, 'Kompyuter Injiniringi', 'kunduzgi', '+998901234567', 'ali@example.com', 'ali_vali', 'secret123'])
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=talabalar_namuna.xlsx'
        
        wb.save(response)
        return response

from django.shortcuts import render
def student_list_view(request):
    return render(request, 'crud_list.html', {'page': 'students'})
