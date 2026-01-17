from django.contrib import admin
from .models import TestResult, StudentAnswer

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'score', 'max_score', 'percentage', 'status', 'started_at')
    list_filter = ('test', 'status', 'started_at')

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question', 'selected_answer', 'is_correct')
