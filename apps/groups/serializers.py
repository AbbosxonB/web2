from rest_framework import serializers
from .models import Group
from apps.accounts.serializers import CustomUserSerializer

class GroupSerializer(serializers.ModelSerializer):
    curator_details = CustomUserSerializer(source='curator', read_only=True)

    class Meta:
        model = Group
        fields = '__all__'
