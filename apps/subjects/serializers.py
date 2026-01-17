from rest_framework import serializers
from .models import Subject
from apps.accounts.serializers import CustomUserSerializer

class SubjectSerializer(serializers.ModelSerializer):
    teacher_details = CustomUserSerializer(source='teacher', read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'
