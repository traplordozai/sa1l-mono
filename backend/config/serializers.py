from rest_framework import serializers
from .models import EnvironmentSetting

class EnvironmentSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentSetting
        fields = ['id', 'mode']
        read_only_fields = ['id']

    def validate_mode(self, value):
        """Validate the environment mode"""
        if value not in dict(EnvironmentSetting.MODE_CHOICES):
            raise serializers.ValidationError(f"Invalid mode: {value}")
        return value

class ChatMessageSerializer(serializers.Serializer):
    """Serializer for chat messages"""
    messages = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            fields=['role', 'content']
        )
    )

    def validate_messages(self, value):
        """Validate the chat messages structure"""
        if not value:
            raise serializers.ValidationError("Messages cannot be empty")
        
        for message in value:
            if 'role' not in message or 'content' not in message:
                raise serializers.ValidationError("Each message must have 'role' and 'content'")
            
            if message['role'] not in ['system', 'user', 'assistant']:
                raise serializers.ValidationError(f"Invalid role: {message['role']}")
        
        return value

class SemanticFilterSerializer(serializers.Serializer):
    """Serializer for semantic filter queries"""
    query = serializers.CharField(required=True)

    def validate_query(self, value):
        """Validate the semantic filter query"""
        if not value.strip():
            raise serializers.ValidationError("Query cannot be empty")
        return value.strip() 