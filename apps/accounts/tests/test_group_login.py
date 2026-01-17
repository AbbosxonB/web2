from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.groups.models import Group
from apps.students.models import Student

User = get_user_model()

class GroupLoginRestrictionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.group = Group.objects.create(
            name="Test Group",
            course=1,
            direction="CS",
            education_form="kunduzgi"
        )
        self.user = User.objects.create_user(
            username="student_user",
            password="password123",
            role="student"
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id="12345",
            full_name="Test Student",
            group=self.group,
            course=1,
            direction="CS",
            education_form="kunduzgi",
            phone="123456789"
        )
        self.login_url = '/api/token/' # Adjust if your URL is different

    def test_login_success_active_group(self):
        self.group.is_system_active = True
        self.group.save()
        response = self.client.post(self.login_url, {
            'username': 'student_user',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_fail_inactive_group(self):
        self.group.is_system_active = False
        self.group.save()
        response = self.client.post(self.login_url, {
            'username': 'student_user',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Sizning guruhingiz tizimga kirishiga ruxsat berilmagan', str(response.data))
