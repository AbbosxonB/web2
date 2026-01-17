from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.groups.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupPaginationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="admin", password="password", role="admin")
        self.client.force_authenticate(user=self.user)
        
        # Create 25 groups
        for i in range(25):
            Group.objects.create(
                name=f"Group {i}",
                course=1,
                direction="CS",
                education_form="kunduzgi"
            )

    def test_pagination(self):
        response = self.client.get('/api/groups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Default page size is 20
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])
