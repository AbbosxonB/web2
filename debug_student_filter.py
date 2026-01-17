import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.students.models import Student
from apps.groups.models import Group

def test_filter():
    # Find a group with students
    groups = Group.objects.all()
    target_group = None
    for g in groups:
        if g.students.count() > 0:
            target_group = g
            break
            
    if not target_group:
        print("No groups with students found.")
        return

    print(f"Target Group: {target_group.name} (ID: {target_group.id})")
    print(f"Expected Student Count: {target_group.students.count()}")

    # Test filtering via ORM (simulating View)
    qs = Student.objects.all()
    # Simulate params
    group_param = str(target_group.id)
    
    filtered_qs = qs.filter(group_id=group_param)
    print(f"Filtered Count (group_id={group_param}): {filtered_qs.count()}")
    
    for s in filtered_qs:
        print(f" - Found Student: {s.full_name} (Group ID: {s.group_id})")

    # Test independent course filter collision?
    # View logic: if course AND group param provided.
    # Frontend sends course param if course filter is set.
    # Does the student course match group course?
    students = target_group.students.all()
    for s in students:
        match = (s.course == target_group.course)
        print(f"Student {s.full_name}: Student Course={s.course}, Group Course={target_group.course} -> Match? {match}")

if __name__ == "__main__":
    test_filter()
