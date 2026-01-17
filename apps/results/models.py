from django.db import models
from django.conf import settings
from apps.students.models import Student
from apps.tests.models import Test, Question

class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    max_score = models.IntegerField()
    percentage = models.FloatField()
    status = models.CharField(max_length=20) # 'passed', 'failed' logic
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    can_retake = models.BooleanField(default=False)
    retake_granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_retakes')

    def __str__(self):
        return f"{self.student.full_name} - {self.test.title}: {self.score}"

class StudentAnswer(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_result.student.full_name} - Q{self.question.id}"
