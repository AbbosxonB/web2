from rest_framework import viewsets, permissions, filters, pagination
from .models import Subject
from .serializers import SubjectSerializer

from django.shortcuts import render

class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    from apps.accounts.granular_permissions import GranularPermission
    permission_classes = [permissions.IsAuthenticated, GranularPermission]
    module_name = 'subjects'
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    def get_queryset(self):
        user = self.request.user
        queryset = Subject.objects.all()
        if user.is_authenticated and user.role == 'teacher':
            return queryset.filter(teacher=user)
            return queryset.filter(teacher=user)
        return queryset

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

    def _log_action(self, action_type, instance, extra_details=None):
        from apps.logs.models import SystemLog
        
        action_map = {
            'create': "Fan yaratildi",
            'update': "Fan tahrirlandi",
            'delete': "Fan o'chirildi"
        }
        
        details = f"Fan: {instance.name}"
        if action_type == 'delete':
             details = f"Fan: {instance.name}"
            
        if extra_details:
             details += f". {extra_details}"
            
        ip = self.request.META.get('REMOTE_ADDR')
        
        SystemLog.objects.create(
            user=self.request.user,
            action=action_map.get(action_type, action_type),
            details=details,
            ip_address=ip
        )

def subject_list_view(request):
    return render(request, 'crud_list.html', {'page': 'subjects'})
