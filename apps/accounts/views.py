from rest_framework import generics, permissions, views, viewsets, filters, pagination
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .serializers import CustomUserSerializer
from apps.students.models import Student
from apps.tests.models import Test
from apps.results.models import TestResult

# DashboardStatsView removed (merged into ProfileView)

class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000
                
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.exclude(role='student')
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can manage employees
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], url_path='update_permissions')
    def update_permissions(self, request, pk=None):
        user = self.get_object()
        permissions_data = request.data.get('permissions', [])
        
        # Clear existing permissions for clean slate or update? 
        # Strategy: update or create based on module
        
        from .models import ModuleAccess
        
        for perm_data in permissions_data:
            module = perm_data.get('module')
            if not module: continue
            
            access, created = ModuleAccess.objects.get_or_create(user=user, module=module)
            
            access.can_view = perm_data.get('can_view', False)
            access.can_create = perm_data.get('can_create', False)
            access.can_update = perm_data.get('can_update', False)
            access.can_delete = perm_data.get('can_delete', False)
            access.can_export = perm_data.get('can_export', False)
            access.save()
            
        return Response({'status': 'Permissions updated'})

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Inject Dashboard Stats
        user = instance
        # Reuse logic from DashboardStatsView (now merged here)
        if user.role == 'admin':
            from datetime import timedelta
            from django.utils import timezone
            from apps.logs.models import SystemLog
            
            now = timezone.now()
            today = now.date()
            last_month = now - timedelta(days=30)

            # 1. Total Students & Growth
            total_students_count = Student.objects.count()
            data['students_count'] = total_students_count
            
            # Growth (last 30 days)
            # Assuming Student model has created_at or we check User date_joined linked to Student?
            # Students are Users with role='student'
            last_month_students_count = CustomUser.objects.filter(role='student', date_joined__lte=last_month).count()
            
            if last_month_students_count > 0:
                growth = ((total_students_count - last_month_students_count) / last_month_students_count) * 100
                data['students_growth'] = f"{growth:.1f}%"
            else:
                data['students_growth'] = "100%" if total_students_count > 0 else "0%"

            # 2. Total Tests & New Tests
            data['tests_count'] = Test.objects.count()
            # New tests in last 24 hours
            last_day = now - timedelta(days=1)
            new_tests_count = Test.objects.filter(created_at__gte=last_day).count()
            data['new_tests_count'] = new_tests_count
            
            data['results_count'] = TestResult.objects.count()
            
            # Logs (Recent Activity)
            logs = SystemLog.objects.select_related('user').order_by('-timestamp')[:5]
            data['logs'] = [{
                'action': log.action,
                'details': log.details,
                'user': log.user.username if log.user else 'Tizim',
                'timestamp': log.timestamp
            } for log in logs]
            
            # Active Tests
            active_tests = Test.objects.filter(status='active').order_by('-start_date')[:5]
            data['active_tests'] = [{
                'id': t.id,
                'title': t.title,
                'group': '...', 
                'start_date': t.start_date
            } for t in active_tests]

            # Stats Cards Data
            data['today_tests_count'] = Test.objects.filter(start_date__date=today).count()
            completed_tests_count = Test.objects.filter(end_date__lt=now).count()
            data['completed_tests_count'] = completed_tests_count
            data['scheduled_tests_count'] = Test.objects.filter(start_date__gt=now).count()
            
            # Additional visual indicators
            data['active_tests_count'] = Test.objects.filter(start_date__lte=now, end_date__gte=now).count()
            
            # Pass/Fail Ratio & Percentage
            passed = TestResult.objects.filter(status='passed').count()
            failed = TestResult.objects.filter(status='failed').count()
            total_results = passed + failed # Ignoring 'not_attended' for ratio calc for now as it's not a status in Result
            
            if total_results > 0:
                pass_rate = (passed / total_results) * 100
                data['pass_rate'] = f"{pass_rate:.1f}%"
            else:
                data['pass_rate'] = "0%"
            
            # Next scheduled test
            next_test = Test.objects.filter(start_date__gt=now).order_by('start_date').first()
            if next_test:
                 delta = next_test.start_date - now
                 data['next_test_in_days'] = delta.days
            else:
                 data['next_test_in_days'] = '-'

            # Chart Data 1: Monthly Dynamics (Aggregated)
            # Simplified aggregation for last 30 days
            chart_data = []
            chart_labels = []
            for i in range(6): # 6 points, every 5 days approx
                d_end = now - timedelta(days=i*5)
                d_start = d_end - timedelta(days=5)
                count = Test.objects.filter(start_date__gte=d_start, start_date__lte=d_end).count()
                chart_labels.insert(0, d_end.strftime('%d-%b'))
                chart_data.insert(0, count)
            
            data['chart_monthly_labels'] = chart_labels
            data['chart_monthly_data'] = chart_data

            # Chart Data 2: Pie
            data['chart_pie_data'] = [passed, failed, 0] # Absents not tracked in Result yet
            
        elif user.role == 'student':
            student = getattr(user, 'student_profile', None)
            if student:
                data['my_tests_count'] = TestResult.objects.filter(student=student).count()
                data['average_score'] = 85 
                # Results for chart
                results = TestResult.objects.filter(student=student).order_by('completed_at')[:5]
                data['chart_labels'] = [r.test.title for r in results]
                data['chart_data'] = [r.percentage for r in results]

        return Response(data)

def login_view(request):
    return render(request, 'auth/login.html')

def dashboard_view(request):
    # Relies on client-side token check
    return render(request, 'dashboard/index.html', {'page': 'dashboard'})

def employee_list_view(request):
    return render(request, 'crud_list.html', {'page': 'employees'})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
