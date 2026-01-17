from rest_framework import serializers
from .models import TestResult, StudentAnswer
from apps.students.serializers import StudentSerializer
from apps.tests.serializers import TestSerializer, QuestionSerializer

class StudentAnswerSerializer(serializers.ModelSerializer):
    question_details = QuestionSerializer(source='question', read_only=True)
    
    class Meta:
        model = StudentAnswer
        fields = '__all__'

class TestResultSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    test_details = TestSerializer(source='test', read_only=True)
    answers = StudentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = TestResult
        fields = '__all__'
