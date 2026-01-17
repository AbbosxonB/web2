import os
import django
from django.test import Client
from django.contrib.auth import get_user_model
from apps.results.models import TestResult
from apps.tests.models import Test
from apps.students.models import Student
from apps.groups.models import Group

from rest_framework_simplejwt.tokens import RefreshToken

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# django.setup()

User = get_user_model()
client = Client()

# Setup Admin User
username = 'test_admin_results_filter'
password = 'test_password'
if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, password=password, role='admin')
else:
    user = User.objects.get(username=username)

# Generate Token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

# client.force_login(user) # Doesn't work without SessionAuthentication

# Get some IDs for testing if data exists
test_id = Test.objects.first().id if Test.objects.exists() else None
group_id = Group.objects.first().id if Group.objects.exists() else None

print(f"Testing Filters with Test ID: {test_id}, Group ID: {group_id}")

# 1. Test Filter
if test_id:
    response = client.get(f'/api/results/?test={test_id}', **auth_headers)
    print(f"Test Filter Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"Passed Test Filter Count: {len(results) if isinstance(results, list) else results.get('count')}")

# 2. Status Filter
response = client.get('/api/results/?status=passed', **auth_headers)
print(f"Status=passed Filter Status: {response.status_code}")
count_passed = 0
if response.status_code == 200:
    results = response.json()
    count_passed = len(results) if isinstance(results, list) else results.get('count')
    print(f"Passed Status Filter Count: {count_passed}")

# 3. Group Filter
if group_id:
    response = client.get(f'/api/results/?student__group={group_id}', **auth_headers)
    print(f"Group Filter Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"Group Filter Count: {len(results) if isinstance(results, list) else results.get('count')}")

# 4. Search Filter
response = client.get('/api/results/?search=student_admin', **auth_headers) # Assuming some student name match
print(f"Search Status: {response.status_code}")

