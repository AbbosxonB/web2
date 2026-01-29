
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.serializers import CustomUserSerializer
from .models import Student
from apps.groups.serializers import GroupSerializer

User = get_user_model()

class StudentSerializer(serializers.ModelSerializer):
    group_details = GroupSerializer(source='group', read_only=True)
    # Extra fields for user creation
    username = serializers.CharField(source='user.username', read_only=True)
    password = serializers.CharField(write_only=False, required=False, source='plain_password')

    class Meta:
        model = Student
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}} # Make user read-only

    def create(self, validated_data):
        # Username handling (for creation logic if needed separate from source)
        # Note: source='user.username' makes username read-only in fields list by default flow if not handled carefully
        # But we need to accept it for creation. So we might need to change approach or just use request data manually.
        # However, to keep it simple and consistent with previous logic:
        
        request = self.context.get('request')
        raw_username = request.data.get('username') if request else None
        raw_password = request.data.get('password')
        
        # Validated data will contain plain_password because of source mapping if it was in input and write_only=False
        # But we also need it for User creation.
        
        password = raw_password or 'student_password'
        username = raw_username or validated_data.get('student_id')
            
        user = User.objects.create_user(username=username, password=password, role='student')
        
        # Determine is_active status
        if 'is_system_active' in validated_data:
             user.is_active = validated_data['is_system_active']
             user.save()

        # Create student with plain_password set automatically if passed to serializer, or manually here
        validated_data['plain_password'] = password
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        # Sync is_system_active with User
        if 'is_system_active' in validated_data:
            instance.user.is_system_active = validated_data['is_system_active']
            instance.user.is_active = validated_data['is_system_active'] # Also update standard Django active status
            instance.user.save()
        
        # Handle password update
        new_password = validated_data.get('plain_password')
        if new_password:
            instance.user.set_password(new_password)
            instance.user.save()
            # plain_password is automatically updated on instance by serializer from validated_data
            
        return super().update(instance, validated_data)
