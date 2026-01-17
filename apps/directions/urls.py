from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectionViewSet, direction_list_view

router = DefaultRouter()
router.register(r'', DirectionViewSet)

urlpatterns = [
    path('list/', direction_list_view, name='direction_list'),
    path('', include(router.urls)),
]
