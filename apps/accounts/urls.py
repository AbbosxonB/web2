from django.urls import path
from .views import ProfileView, login_view, dashboard_view

urlpatterns = [
    path('', login_view, name='home'), # Handle root URL
    path('profile/', ProfileView.as_view(), name='profile'),
    # Template views
    path('login/', login_view, name='login_page'),
    path('dashboard/', dashboard_view, name='dashboard'),
]
