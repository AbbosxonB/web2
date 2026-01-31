from django.db import models
from django.conf import settings
from apps.subjects.models import Subject
from apps.groups.models import Group

class Test(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Rejada'),
        ('active', 'Faol'),
        ('completed', 'Yakunlangan'),
        ('paused', 'Pauza'),
    )
    
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tests')
    groups = models.ManyToManyField(Group, through='TestAssignment', related_name='tests')
    questions_count = models.IntegerField(default=25)
    duration = models.IntegerField(help_text="Daqiqada")
    max_score = models.IntegerField(default=50)
    passing_score = models.IntegerField(default=30)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    allow_mobile_access = models.BooleanField(default=True, help_text="Telefondan kirishga ruxsat berish")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_tests')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    score = models.IntegerField(default=2)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.test.title}: {self.question_text[:50]}"

class TestAssignment(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.test.title} - {self.group.name}"

class TestSnapshot(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='snapshots')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='snapshots')
    image = models.ImageField(upload_to='snapshots/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.timestamp}"
