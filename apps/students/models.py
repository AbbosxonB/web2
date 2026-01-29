from django.db import models
from django.conf import settings

class Student(models.Model):
    EDUCATION_FORMS = (
        ('kunduzgi', 'Kunduzgi'),
        ('sirtqi', 'Sirtqi'),
        ('kechki', 'Kechki'),
    )
    
    STATUSES = (
        ('active', 'Faol'),
        ('academic_leave', 'Akademik ta\'til'),
        ('expelled', 'O\'qishni to\'xtatgan'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, related_name='students')
    course = models.IntegerField()
    direction = models.CharField(max_length=255)
    education_form = models.CharField(max_length=20, choices=EDUCATION_FORMS)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='active')
    is_system_active = models.BooleanField(default=True)
    hemis_synced = models.BooleanField(default=False)
    plain_password = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.group})"
