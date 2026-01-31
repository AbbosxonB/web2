import os
import django
import sys
from django.test import RequestFactory
from rest_framework.request import Request

# Setup Django environment
sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tests.views import TestViewSet
from apps.results.models import TestResult
from apps.students.models import Student

# Get the student with the in_progress result (ID 36 implies there's a result)
# Let's find the result first
in_progress_result = TestResult.objects.filter(status='in_progress').last()

if not in_progress_result:
    print("No in_progress result found to test specific resume logic.")
    # Try to find a student/test combo to create one?
    # For now, let's just list students.
    student = Student.objects.first()
    print(f"Using random student: {student.full_name}")
else:
    student = in_progress_result.student
    test = in_progress_result.test
    print(f"Testing Resume for Student: {student.full_name}, Test: {test.title}")
    
    # Mock Request
    factory = RequestFactory()
    request = factory.get(f'/api/tests/{test.id}/start/')
    request.user = student.user
    
    # Initialize ViewSet
    view = TestViewSet.as_view({'get': 'start_test'})
    
    # Run View
    try:
        response = view(request, pk=test.id)
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Test started (or resumed) successfully.")
            print(f"Data keys: {response.data.keys()}")
        else:
            print(f"FAILURE: {response.data}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
