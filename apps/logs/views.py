from rest_framework import viewsets, permissions
from .models import SystemLog
from .serializers import SystemLogSerializer

class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAdminUser]

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def log_system_view(request):
    return render(request, 'crud_list.html', {'page': 'log_system'})
