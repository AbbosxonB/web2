import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import TestResult
from apps.students.models import Student
from apps.tests.models import Test

print("--- Checking Database State ---")
# Check for any results that might be blocking
# We'll just look at the most recent results or all results for a test that has issues.
# Since we don't know the exact student/test, let's list the ones with recent activity.

print("\nRecent TestResults (Last 10):")
results = TestResult.objects.all().order_by('-id')[:10]
for res in results:
    print(f"ID: {res.id}, Student: {res.student.full_name} (ID: {res.student.id}), Test: {res.test.title}, Status: {res.status}, Can Retake: {res.can_retake}")

print("\n--- Checking for duplicates/zombies ---")
# Count results per student/test
from django.db.models import Count
dupes = TestResult.objects.values('student', 'test').annotate(count=Count('id')).filter(count__gt=1)
for d in dupes:
    print(f"Duplicate found: Student ID {d['student']} - Test ID {d['test']} has {d['count']} results.")

# Also check "in_progress" specifically
in_progress = TestResult.objects.filter(status='in_progress')
print(f"\nIn Progress Results: {in_progress.count()}")
for res in in_progress:
    print(f"ID: {res.id}, Student: {res.student.full_name}, Test: {res.test.title}")
