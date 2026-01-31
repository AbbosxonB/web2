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
        return queryset

def subject_list_view(request):
    return render(request, 'crud_list.html', {'page': 'subjects'})
