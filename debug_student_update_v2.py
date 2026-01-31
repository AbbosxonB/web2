import os
import django
import sys
import json

sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.students.models import Student

User = get_user_model()
admin = User.objects.filter(role='admin').first()

if not admin:
    print("No admin user found.")
    sys.exit(1)

c = Client()
c.force_login(admin)

s = Student.objects.first()
if not s:
    print("No students.")
    sys.exit(1)

print(f"--- PATCHing Student {s.id} ---")
response = c.patch(f'/api/students/{s.id}/', data={'is_system_active': False}, content_type='application/json')

print(f"Status: {response.status_code}")
if response.status_code != 200:
    try:
        data = json.loads(response.content.decode())
        print("Validation Errors:")
        print(json.dumps(data, indent=2))
    except:
        print("Raw Content:")
        print(response.content.decode())
else:
    print("Success (200)")
