from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemLogViewSet

router = DefaultRouter()
router.register(r'', SystemLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
