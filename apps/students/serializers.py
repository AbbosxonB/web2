
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.serializers import CustomUserSerializer
from .models import Student
from apps.groups.serializers import GroupSerializer

User = get_user_model()

class StudentSerializer(serializers.ModelSerializer):
    group_details = GroupSerializer(source='group', read_only=True)
    # Extra fields for user creation
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Student
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}} # Make user read-only

    def create(self, validated_data):
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        
        # If no username provided, generate from student_id
        if not username:
            username = validated_data.get('student_id')
        if not password:
            password = 'student_password' # Default password if not set
            
        user = User.objects.create_user(username=username, password=password, role='student')
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        # Sync is_system_active with User
        if 'is_system_active' in validated_data:
            instance.user.is_system_active = validated_data['is_system_active']
            instance.user.is_active = validated_data['is_system_active'] # Also update standard Django active status
            instance.user.save()
            
        return super().update(instance, validated_data)
