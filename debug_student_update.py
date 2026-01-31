import requests
import json
import os
import django
import sys

# Setup Django to get User model (optional, just for credentials if needed, but requests is external)
# actually we can just use requests against localhost:8000

BASE_URL = 'http://localhost:8000'

def login(username, password):
    url = f"{BASE_URL}/api/token/"
    resp = requests.post(url, data={'username': username, 'password': password})
    if resp.status_code == 200:
        return resp.json()['access_token']
    else:
        print(f"Login failed: {resp.text}")
        return None

def test_patch_student(token, student_id):
    url = f"{BASE_URL}/api/students/{student_id}/"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {'is_system_active': False}
    
    print(f"Sending PATCH to {url} with {data}")
    resp = requests.patch(url, headers=headers, json=data)
    
    print(f"Status Code: {resp.status_code}")
    print(f"Response Body: {resp.text}")

# Credentials - Assuming admin/admin or trying to find one from DB
# I will use django to find a superuser
sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.filter(role='admin').first()
if not admin:
    print("No admin user found.")
    sys.exit(1)

# Note: I don't have the plain password for admin. 
# I can set a temp password or create a temp superuser via script?
# Or just try to use a known user if I knew one.
# Alternative: Use 'force_login' approach with Django Test Client instead of requests?
# YES, Django Test Client is better because I don't need password.

print(f"Using Django Test Client with user: {admin.username}")

from django.test import Client
c = Client()
c.force_login(admin)

student_id = 5409 # From user logs
# Check if student exists
from apps.students.models import Student
if not Student.objects.filter(id=student_id).exists():
    print(f"Student {student_id} not found, finding first available student.")
    s = Student.objects.first()
    if s:
        student_id = s.id
        print(f"Using student ID: {student_id}")
    else:
        print("No students in DB.")
        sys.exit(1)

print(f"Attempting PATCH /api/students/{student_id}/")
response = c.patch(f'/api/students/{student_id}/', data={'is_system_active': False}, content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Content: {response.content.decode()}")

