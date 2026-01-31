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
