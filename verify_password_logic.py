import os
import django
from unittest.mock import Mock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.students.models import Student
from django.contrib.auth import get_user_model
from apps.students.serializers import StudentSerializer

User = get_user_model()

# Cleanup test data
test_username = 'test_student_verify'
Student.objects.filter(user__username=test_username).delete()
User.objects.filter(username=test_username).delete()

# Create dummy data for serializer
data = {
    'student_id': '123456789',
    'full_name': 'Test Student Verify',
    'course': 1,
    'direction': 'Test Direction',
    'education_form': 'kunduzgi',
    'phone': '+998901234567',
    'username': test_username,
    'password': 'plain_text_password_123',
    'is_system_active': True
}

# Mock request
mock_request = Mock()
mock_request.data = data

print("Creating student via serializer...")
# Pass mock request to context to satisfy serializer logic
serializer = StudentSerializer(data=data, context={'request': mock_request})

if serializer.is_valid():
    student = serializer.save()
    print("Student created successfully.")
    
    # Reload from DB
    student.refresh_from_db()
    
    print(f"Stored Plain Password: {student.plain_password}")
    print(f"User Active: {student.user.is_active}")
    print(f"Username: {student.user.username}")
    
    if student.plain_password == 'plain_text_password_123':
        print("PASS: Plain password stored correctly.")
    else:
        print("FAIL: Plain password mismatch.")
        
    if student.user.check_password('plain_text_password_123'):
         print("PASS: User hashed password works.")
    else:
         print("FAIL: User hashed password mismatch.")

else:
    print("Serializer Errors:", serializer.errors)
