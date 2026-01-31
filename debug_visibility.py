import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from apps.tests.models import Test
from apps.groups.models import Group
from apps.students.models import Student
from django.contrib.auth import get_user_model

User = get_user_model()

print("--- ALL TESTS ---")
tests = Test.objects.all()
if not tests.exists():
    print("No tests found in database!")
else:
    for t in tests:
        print(f"ID: {t.id} | Title: {t.title} | Status: {t.status} | Subject: {t.subject}")
        groups = t.groups.all()
        group_names = ", ".join([g.name for g in groups])
        print(f"   -> Assigned Groups: {group_names if group_names else 'NONE'}")

print("\n--- SAMPLE STUDENTS ---")
students_users = User.objects.filter(role='student')[:5]
for u in students_users:
    if hasattr(u, 'student_profile'):
        print(f"User: {u.username} | Group: {u.student_profile.group}")
    else:
        print(f"User: {u.username} | NO PROFILE")

print("\n--- DIAGNOSIS ---")
# Check if any active test is assigned to a group that has students
active_tests = Test.objects.filter(status='active')
if not active_tests.exists():
    print("WARNING: No tests have status='active'. Students only see active tests.")
else:
    for t in active_tests:
        print(f"Test '{t.title}' is ACTIVE.")
        if t.groups.exists():
            print(f"   It is assigned to: {', '.join([g.name for g in t.groups.all()])}")
        else:
            print("   WARNING: Not assigned to any groups!")
