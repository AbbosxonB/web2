from django.contrib import admin
from .models import Group

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'direction', 'education_form', 'curator', 'is_system_active')
    search_fields = ('name', 'direction')
    list_filter = ('course', 'education_form', 'is_system_active')
