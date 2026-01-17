from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    courses = models.CharField(max_length=100, help_text="Vergul bilan ajratilgan kurslar (1,2,3)")
    directions = models.TextField(help_text="Yo'nalishlar ro'yxati")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
