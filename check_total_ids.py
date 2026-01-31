import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import TestResult

count = TestResult.objects.count()
print(f"Total TestResults in Database: {count}")

print("IDs:")
for res in TestResult.objects.all().order_by('id'):
    print(f"- ID: {res.id} | Student: {res.student.full_name} | Test: {res.test.title} | Status: {res.status}")
