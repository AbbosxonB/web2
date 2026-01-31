import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from apps.tests.models import Test, TestAssignment
from apps.groups.models import Group

# Find the target group
try:
    target_group = Group.objects.get(name='BTSIR-22')
    print(f"Found target group: {target_group.name} (ID: {target_group.id})")
except Group.DoesNotExist:
    print("Error: Group 'BTSIR-22' not found. Please verify the group name.")
    sys.exit(1)

# Find active tests
active_tests = Test.objects.filter(status='active')
print(f"Found {active_tests.count()} active tests.")

for test in active_tests:
    # Assign to group
    obj, created = TestAssignment.objects.get_or_create(test=test, group=target_group)
    if created:
        print(f"Assigned test '{test.title}' to group '{target_group.name}'")
    else:
        print(f"Test '{test.title}' already assigned to '{target_group.name}'")

print("Done. Please refresh the student page.")
