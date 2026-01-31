import os
import django
import sys

sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.monitoring.models import GlobalSetting
from apps.students.models import Student

print("--- GLOBAL SETTINGS ---")
try:
    setting = GlobalSetting.objects.get(key='camera_required_globally')
    print(f"Key: {setting.key}")
    print(f"Value: '{setting.value}' (Type: {type(setting.value)})")
except GlobalSetting.DoesNotExist:
    print("GlobalSetting 'camera_required_globally' DOES NOT EXIST.")

print("\n--- SAMPLE STUDENTS ---")
students = Student.objects.all()[:5]
for s in students:
    print(f"Student: {s.full_name}")
    print(f"  Camera Mode: '{s.camera_mode}'")
    
    # Simulate Logic
    camera_required = False
    if s.camera_mode == 'required':
        camera_required = True
    elif s.camera_mode == 'not_required':
        camera_required = False
    else:
        # Default
        try:
             gs = GlobalSetting.objects.get(key='camera_required_globally')
             val = gs.value
             camera_required = (val == 'true')
             print(f"  -> Using Global ('{val}'): {camera_required}")
        except:
             camera_required = False
             print(f"  -> Global invalid/missing. Defaulting False.")
             
    print(f"  -> FINAL: is_camera_required = {camera_required}")
