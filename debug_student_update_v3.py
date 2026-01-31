import os
import django
import sys
import json
import uuid
import traceback

sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.students.models import Student

User = get_user_model()

# Create a fresh admin to be sure
username = f'debug_admin_{uuid.uuid4().hex[:8]}'
admin = User.objects.create_superuser(username, 'admin@example.com', 'password')
admin.role = 'admin' # Ensure role is set
admin.save()

print(f"Created admin: {admin.username} (Role: {admin.role})", flush=True)

c = Client()
c.force_login(admin)

s = Student.objects.first()
if not s:
    print("No students.")
    sys.exit(1)

print(f"--- PATCHing Student {s.id} ---", flush=True)

try:
    response = c.patch(
        f'/api/students/{s.id}/', 
        data={'is_system_active': False}, 
        content_type='application/json'
    )
    print(f"Status: {response.status_code}", flush=True)
    
    if response.status_code != 200:
        try:
            content = response.content.decode()
            print("Response Content:", flush=True)
            print(content, flush=True)
            
            try:
                data = json.loads(content)
                print("Parsed JSON:", flush=True)
                print(json.dumps(data, indent=2), flush=True)
            except:
                pass
        except Exception as e:
            print(f"Error reading response: {e}", flush=True)
    else:
        print("Success (200)", flush=True)
        
except Exception as e:
    print(f"CRASH: {e}", flush=True)
    traceback.print_exc()
