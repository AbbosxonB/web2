from rest_framework import serializers
from .models import CustomUser, ModuleAccess

class ModuleAccessSerializer(serializers.ModelSerializer):
    module_display = serializers.CharField(source='get_module_display', read_only=True)

    class Meta:
        model = ModuleAccess
        fields = ['id', 'module', 'module_display', 'can_view', 'can_update', 'can_create', 'can_delete', 'can_export']

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    permissions = ModuleAccessSerializer(source='module_accesses', many=True, required=False)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name', 'role', 'phone', 'photo', 'language', 'password', 'permissions', 'is_active', 'is_system_active')

    def get_full_name(self, obj):
        if obj.role == 'student' and hasattr(obj, 'student_profile'):
            return obj.student_profile.full_name
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.username

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        permissions_data = validated_data.pop('module_accesses', [])
        
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
            
        for perm in permissions_data:
            ModuleAccess.objects.create(user=user, **perm)
            
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        permissions_data = validated_data.pop('module_accesses', None)
        
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        if permissions_data is not None:
            # Simple strategy: clear old and re-create, or update in place.
            # Re-creating ensures clean slate. 
            instance.module_accesses.all().delete()
            for perm in permissions_data:
                ModuleAccess.objects.create(user=instance, **perm)
            
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
