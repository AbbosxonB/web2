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

    duration = serializers.SerializerMethodField()
    formatted_completed_at = serializers.SerializerMethodField()

    def get_duration(self, obj):
        if obj.completed_at and obj.started_at:
            diff = obj.completed_at - obj.started_at
            total_seconds = int(diff.total_seconds())
            if total_seconds < 60:
                return f"{total_seconds} sek"
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes} min {seconds} sek"
        return "N/A"

    def get_formatted_completed_at(self, obj):
        from django.utils import timezone
        if obj.completed_at:
            local_dt = timezone.localtime(obj.completed_at)
            return local_dt.strftime("%d.%m.%Y %H:%M")
        return "-"
