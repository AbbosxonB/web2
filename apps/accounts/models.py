from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('admin', 'Bosh Admin'),
        ('dean', 'Dekan'),
        ('teacher', 'O\'qituvchi'),
        ('student', 'Talaba'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    student_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_system_active = models.BooleanField(default=True)
    failed_login_attempts = models.IntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=10, default='uz')
    photo = models.ImageField(upload_to='users/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class ModuleAccess(models.Model):
    MODULE_CHOICES = (
        ('dashboard', 'Dashboard'),
        ('tasks', 'Vazifalar'),
        ('applicants', 'Arizachilar'),
        ('second_specialty', 'Ikkinchi mutaxassislik'),
        ('transfer', 'O\'qishni ko\'chirish'),
        ('contract_given', 'Shartnoma berilgan'),
        ('course_applications', 'Kurs arizalari'),
        ('registered', 'Ro\'yxatdan o\'tganlar'),
        ('offered', 'Taklif qilganlar'),
        ('tests', 'Testlar'),
        ('groups', 'Guruhlar'),
        ('students', 'Talabalar'),
        ('employees', 'Xodimlar'),
        ('log_system', 'Loglar'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='module_accesses')
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    
    can_view = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'module')

    def __str__(self):
        return f"{self.user.username} - {self.get_module_display()}"
