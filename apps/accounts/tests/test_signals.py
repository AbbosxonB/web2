from django.test import TestCase
from apps.accounts.models import CustomUser, ModuleAccess

class PermissionSignalTest(TestCase):
    def test_default_permissions_dean(self):
        user = CustomUser.objects.create_user(
            username='dean_test', 
            password='password123',
            role='dean'
        )
        # Check permissions
        self.assertTrue(user.module_accesses.exists())
        self.assertTrue(user.module_accesses.filter(module='students', can_view=True).exists())
        self.assertTrue(user.module_accesses.filter(module='employees', can_view=True).exists())

    def test_default_permissions_teacher(self):
        user = CustomUser.objects.create_user(
            username='teacher_test', 
            password='password123',
            role='teacher'
        )
        self.assertTrue(user.module_accesses.exists())
        self.assertTrue(user.module_accesses.filter(module='tests', can_view=True).exists())
        # Teachers shouldn't have full admin access by default unless specified
        self.assertFalse(user.module_accesses.filter(module='employees', can_view=True).exists())

    def test_default_permissions_student(self):
         user = CustomUser.objects.create_user(
            username='student_test', 
            password='password123',
            role='student'
        )
         self.assertTrue(user.module_accesses.exists())
         self.assertTrue(user.module_accesses.filter(module='results', can_view=True).exists())
