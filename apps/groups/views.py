from rest_framework import viewsets, permissions, filters, pagination
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
    permission_classes = [permissions.IsAuthenticated]
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

def group_list_view(request):
    return render(request, 'crud_list.html', {'page': 'groups'})
