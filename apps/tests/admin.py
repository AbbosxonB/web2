from django.contrib import admin
from .models import Test, Question, TestAssignment

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'start_date', 'end_date', 'status', 'questions_count')
    list_filter = ('status', 'subject', 'created_at')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'question_text', 'correct_answer', 'score')
    list_filter = ('test',)

@admin.register(TestAssignment)
class TestAssignmentAdmin(admin.ModelAdmin):
    list_display = ('test', 'group', 'start_time', 'end_time')
