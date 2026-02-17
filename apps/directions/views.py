from rest_framework import viewsets, permissions, filters, pagination
from .models import Direction
from .serializers import DirectionSerializer
from django.shortcuts import render

class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class DirectionViewSet(viewsets.ModelViewSet):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
    from apps.accounts.granular_permissions import GranularPermission
    permission_classes = [permissions.IsAuthenticated, GranularPermission]
    module_name = 'directions'
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

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
            'create': "Yo'nalish yaratildi",
            'update': "Yo'nalish tahrirlandi",
            'delete': "Yo'nalish o'chirildi"
        }
        
        details = f"Yo'nalish: {instance.name} (Code: {instance.code})"
        if action_type == 'delete':
             details = f"Yo'nalish: {instance.name} (Code: {instance.code})"
            
        if extra_details:
             details += f". {extra_details}"
            
        ip = self.request.META.get('REMOTE_ADDR')
        
        SystemLog.objects.create(
            user=self.request.user,
            action=action_map.get(action_type, action_type),
            details=details,
            ip_address=ip
        )

def direction_list_view(request):
    return render(request, 'crud_list.html', {'page': 'directions'})
