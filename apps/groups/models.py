from django.db import models
from django.conf import settings

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    course = models.IntegerField()
    direction = models.CharField(max_length=255)
    education_form = models.CharField(max_length=20)
    curator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='curated_groups')
    is_system_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
