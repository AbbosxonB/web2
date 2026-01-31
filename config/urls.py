"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from apps.accounts.views import login_view, dashboard_view, ProfileView, EmployeeViewSet, employee_list_view
from apps.students.views import student_list_view, StudentViewSet
from apps.groups.views import group_list_view, GroupViewSet
from apps.accounts.views import login_view, dashboard_view, ProfileView, EmployeeViewSet, employee_list_view
from apps.students.views import student_list_view, StudentViewSet
from apps.groups.views import group_list_view, GroupViewSet
from apps.subjects.views import subject_list_view, SubjectViewSet
from apps.tests.views import test_list_view, TestViewSet, take_test_view, edit_test_view, QuestionViewSet
from apps.results.views import result_list_view, TestResultViewSet
from apps.directions.views import direction_list_view, DirectionViewSet
from apps.accounts.views import CustomTokenObtainPairView
from apps.monitoring.views import monitoring_page_view
from apps.logs.views import log_system_view

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'students', StudentViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'directions', DirectionViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'tests', TestViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'results', TestResultViewSet)

urlpatterns = [
    path('tests/take/<int:test_id>/', take_test_view, name='take_test_page'),
    path('take/<int:test_id>/', take_test_view, name='take_test_shortcut'),
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs - specific custom URLs if any, but ViewSets are handled by router above.
    # Keeping them IF they have extra custom paths not in ViewSet, but generally redundant if just ViewSet.
    # However, apps.accounts.urls might have login/profile etc not in router.
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/logs/', include('apps.logs.urls')),
    path('api/monitoring/', include('apps.monitoring.urls')),


    # Frontend Pages
    path('students/', student_list_view, name='students_page'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('employees/', employee_list_view, name='employee_list'),
    path('groups/', group_list_view, name='groups_page'),
    path('subjects/', subject_list_view, name='subjects_page'),
    path('directions/', direction_list_view, name='directions_page'),
    path('tests/', test_list_view, name='tests_page'),
    path('tests/edit/<int:test_id>/', edit_test_view, name='edit_test_page'),

    path('results/', result_list_view, name='results_page'),
    path('results/', result_list_view, name='results_page'),
    path('monitoring/', monitoring_page_view, name='monitoring_page'),
    path('logs/', log_system_view, name='logs_page'),

    # Frontend URLs (Auth/Dash)
    path('', include('apps.accounts.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
