from rest_framework import serializers
from .models import Test, Question, TestAssignment
from apps.subjects.serializers import SubjectSerializer
from apps.groups.serializers import GroupSerializer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class TestAssignmentSerializer(serializers.ModelSerializer):
    group_details = GroupSerializer(source='group', read_only=True)
    
    class Meta:
        model = TestAssignment
        fields = '__all__'

class TestSerializer(serializers.ModelSerializer):
    subject_details = SubjectSerializer(source='subject', read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    assignments = TestAssignmentSerializer(source='testassignment_set', many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'
