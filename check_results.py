import os
import django
import sys

sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import TestResult
from apps.tests.models import Test

print("--- TEST RESULTS ---")
results = TestResult.objects.all().order_by('-started_at')
for r in results:
    print(f"Result ID: {r.id}")
    print(f"  Student: {r.student.full_name}")
    print(f"  Test: {r.test.title} (ID: {r.test.id})")
    print(f"  Score: {r.score}")
    print(f"  Can Retake: {r.can_retake}")
    print(f"  Date: {r.started_at}")
    print("-" * 30)

if not results.exists():
    print("No results found.")
