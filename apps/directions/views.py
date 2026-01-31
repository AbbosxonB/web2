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

def direction_list_view(request):
    return render(request, 'crud_list.html', {'page': 'directions'})
