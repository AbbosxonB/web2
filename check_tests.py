import os
import django
import sys
from django.utils import timezone

sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tests.models import Test

print("--- TESTS ---")
now = timezone.now()
print(f"Current Server Time: {now}")

tests = Test.objects.all()
for t in tests:
    print(f"Test ID: {t.id}")
    print(f"  Title: {t.title}")
    print(f"  Start: {t.start_date}")
    print(f"  End:   {t.end_date}")
    
    status = "ACTIVE"
    if now < t.start_date: status = "NOT STARTED"
    elif now > t.end_date: status = "EXPIRED"
    
    print(f"  Status: {status}")
    print("-" * 30)
