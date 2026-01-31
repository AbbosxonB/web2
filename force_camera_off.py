import os
import django
import sys

sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.monitoring.models import GlobalSetting

print("--- FORCING CAMERA OFF ---")
GlobalSetting.set_value('camera_required_globally', 'false')

s = GlobalSetting.objects.get(key='camera_required_globally')
print(f"New Value: '{s.value}'")
print("Done.")
