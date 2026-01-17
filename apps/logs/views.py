from rest_framework import viewsets, permissions
from .models import SystemLog
from .serializers import SystemLogSerializer

class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAdminUser]
