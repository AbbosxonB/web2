import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.accounts.models import CustomUser
from apps.groups.models import Group

def check_login_restriction(username):
    user = CustomUser.objects.filter(username=username).first()
    if not user:
        print(f"User {username} not found.")
        return

    print(f"User found: {user.username}, Role: {user.role}, Is System Active: {user.is_system_active}")
    
    if user.role == 'student':
        student_profile = getattr(user, 'student_profile', None)
        if student_profile:
            print(f"Student Profile found: {student_profile}")
            if student_profile.group:
                print(f"Group found: {student_profile.group.name}, ID: {student_profile.group.id}, Is System Active: {student_profile.group.is_system_active}")
                
                if not student_profile.group.is_system_active:
                    print("BLOCKED: Group is inactive.")
                else:
                    print("ALLOWED: Group is active.")
            else:
                print("WARNING: Student has no group assigned.")
        else:
            print("WARNING: User has 'student' role but no Student profile.")
    else:
        print("User is not a student.")

# You can modify this to check a specific user that you know is failing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
        check_login_restriction(username)
    else:
        # Check an example student if no arg provided
        # Find a student in an inactive group to test
        inactive_group = Group.objects.filter(is_system_active=False).first()
        if inactive_group:
            student = inactive_group.students.first()
            if student:
                print(f"Testing with student from inactive group '{inactive_group.name}': {student.user.username}")
                check_login_restriction(student.user.username)
            else:
                print(f"Inactive group '{inactive_group.name}' has no students.")
        else:
            print("No inactive groups found.")
