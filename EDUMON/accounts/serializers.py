from rest_framework import serializers

from .models import CustomUser, StatusUpdate


class UserSerializer(serializers.ModelSerializer):
    """Serializes user profile data for the API (R2b, R4)."""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'real_name', 'role', 'bio', 'photo']
        read_only_fields = ['id', 'role']


class StatusUpdateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = StatusUpdate
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
