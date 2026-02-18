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
            
        if education_form:
            queryset = queryset.filter(education_form__iexact=education_form)
            
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e), 'trace': traceback.format_exc()}, status=500)

    def perform_create(self, serializer):
        instance = serializer.save()
        self._log_action('create', instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        changed_fields = [k for k in self.request.data.keys() if k not in ['id', 'csrfmiddlewaretoken']]
        extra = f"O'zgarganlar: {', '.join(changed_fields)}" if changed_fields else "Tahrirlandi"
        self._log_action('update', instance, extra_details=extra)

    def perform_destroy(self, instance):
        self._log_action('delete', instance)
        instance.delete()

    def _log_action(self, action_type, instance=None, extra_details=None):
        from apps.logs.models import SystemLog
        
        action_map = {
            'create': "Talaba yaratildi",
            'update': "Talaba tahrirlandi",
            'delete': "Talaba o'chirildi",
            'import': "Talabalar import qilindi",
            'bulk_update': "Ommaviy o'zgartirish"
        }
        
        details = ""
        if instance:
            details = f"Talaba: {instance.full_name} (ID: {instance.student_id})"
            
        if extra_details:
             details = f"{details}. {extra_details}" if details else extra_details
            
        ip = self.request.META.get('REMOTE_ADDR')
        
        SystemLog.objects.create(
            user=self.request.user,
            action=action_map.get(action_type, action_type),
            details=details,
            ip_address=ip
        )

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
             self._log_action('bulk_update', extra_details=f"{len(ids)} ta talaba o'chirildi")
             return Response({'status': 'deleted', 'count': len(ids)})
             
        elif action == 'activate':
            queryset.update(is_system_active=True)
            self._log_action('bulk_update', extra_details=f"{len(ids)} ta talaba faollashtirildi")
            return Response({'status': 'activated', 'count': len(ids)})
            
        elif action == 'deactivate':
            queryset.update(is_system_active=False)
            self._log_action('bulk_update', extra_details=f"{len(ids)} ta talaba nofaol qilindi")
            return Response({'status': 'deactivated', 'count': len(ids)})
            
        return Response({'error': 'Noto\'g\'ri amal'}, status=400)

    @decorators.action(detail=False, methods=['post'], url_path='import')
    def import_students(self, request):
        try:
            file = request.FILES.get('file')
            if not file: return Response({'error': 'Fayl tanlanmadi'}, status=400)
            
            from .excel_import import import_students_from_excel
            count = import_students_from_excel(file)
            self._log_action('import', extra_details=f"{count} ta talaba yuklandi")
            return Response({'status': 'success', 'count': count})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': f"Xatolik yuz berdi: {str(e)}"}, status=400)

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
