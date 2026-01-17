from rest_framework import serializers
from .models import CustomUser, ModuleAccess

class ModuleAccessSerializer(serializers.ModelSerializer):
    module_display = serializers.CharField(source='get_module_display', read_only=True)

    class Meta:
        model = ModuleAccess
        fields = ['id', 'module', 'module_display', 'can_view', 'can_update', 'can_create', 'can_delete', 'can_export']

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    permissions = ModuleAccessSerializer(source='module_accesses', many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'role', 'phone', 'photo', 'language', 'password', 'permissions', 'is_active', 'is_system_active')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get('password')

        if username and password:
            user = CustomUser.objects.filter(username=username).first()
            if user and user.check_password(password):
                if not user.is_active:
                    raise AuthenticationFailed('Sizga tizimga kirishga ruxsat berilmagan. Dekanatga murojaat qiling!')

        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            raise AuthenticationFailed("Login yoki parol noto'g'ri")
        
        if self.user.role == 'student':
            student_profile = getattr(self.user, 'student_profile', None)
            if student_profile and student_profile.group and not student_profile.group.is_system_active:
                raise AuthenticationFailed('Sizning guruhingiz tizimga kirishiga ruxsat berilmagan. Dekanatga murojaat qiling!')

        if not self.user.is_system_active:
            raise AuthenticationFailed('Sizning hisobingiz faol emas. Iltimos administratorga murojaat qiling.')
            
        return data
