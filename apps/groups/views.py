from rest_framework import viewsets, permissions, filters, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Group
from .serializers import GroupSerializer

from django.shortcuts import render

class GroupPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    from apps.accounts.granular_permissions import GranularPermission
    permission_classes = [permissions.IsAuthenticated, GranularPermission]
    module_name = 'groups'
    pagination_class = GroupPagination
    filter_backends = [filters.SearchFilter]
    ordering = ['name']

    def perform_create(self, serializer):
        instance = serializer.save()
        self._log_action('create', instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Detect changes roughly
        changed_fields = [k for k in self.request.data.keys() if k not in ['id', 'csrfmiddlewaretoken']]
        extra = f"O'zgarganlar: {', '.join(changed_fields)}" if changed_fields else "Tahrirlandi"
        self._log_action('update', instance, extra_details=extra)

    def perform_destroy(self, instance):
        self._log_action('delete', instance)
        instance.delete()

    def _log_action(self, action_type, instance, extra_details=None):
        from apps.logs.models import SystemLog
        
        action_map = {
            'create': "Guruh yaratildi",
            'update': "Guruh tahrirlandi",
            'delete': "Guruh o'chirildi"
        }
        
        details = f"Guruh: {instance.name} (ID: {instance.id})"
        if action_type == 'delete':
            details = f"Guruh: {instance.name} (ID: {instance.id})"
            
        if extra_details:
            details += f". {extra_details}"
            
        ip = self.request.META.get('REMOTE_ADDR')
        
        SystemLog.objects.create(
            user=self.request.user,
            action=action_map.get(action_type, action_type),
            details=details,
            ip_address=ip
        )
    search_fields = ['name', 'direction']

    def get_queryset(self):
        queryset = Group.objects.all()
        course = self.request.query_params.get('course')
        direction = self.request.query_params.get('direction')
        
        is_active = self.request.query_params.get('is_system_active')
        
        if course:
            queryset = queryset.filter(course=course)
        if direction:
            queryset = queryset.filter(direction__icontains=direction)
        if is_active is not None:
             # Convert string 'true'/'false' to boolean
             is_active_bool = is_active.lower() == 'true'
             queryset = queryset.filter(is_system_active=is_active_bool)
            
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        user = request.user
        if user.role != 'admin' and (not user.permissions or not any(p.module == 'groups' and p.can_update for p in user.permissions)):
             return Response({'error': 'Huquq yo\'q'}, status=403)
        
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'error': 'Hech narsa tanlanmadi'}, status=400)
            
        queryset = Group.objects.filter(id__in=ids)
        
        if action == 'delete':
             if user.role != 'admin' and (not user.permissions or not any(p.module == 'groups' and p.can_delete for p in user.permissions)):
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

def group_list_view(request):
    return render(request, 'crud_list.html', {'page': 'groups'})
