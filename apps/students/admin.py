from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'student_id', 'group', 'course', 'status', 'is_system_active')
    search_fields = ('full_name', 'student_id', 'phone')
    list_filter = ('status', 'education_form', 'course', 'group')
