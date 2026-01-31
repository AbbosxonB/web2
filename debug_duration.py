import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import TestResult
from django.utils import timezone

print(f"Current Time (Local): {timezone.localtime(timezone.now())}")
print(f"Current Time (UTC): {timezone.now()}")

print("\n--- Recent Test Results ---")
# Get last 5 results
results = TestResult.objects.all().order_by('-id')[:5]

for res in results:
    print(f"ID: {res.id}, Status: {res.status}")
    print(f"  Started:   {res.started_at}")
    print(f"  Completed: {res.completed_at}")
    if res.started_at and res.completed_at:
        diff = res.completed_at - res.started_at
        print(f"  Diff: {diff}")
        print(f"  Seconds: {diff.total_seconds()}")
    else:
        print("  Duration: N/A (Missing timestamps)")
    print("-" * 30)
