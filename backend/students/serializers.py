from rest_framework import serializers
from .models import Student
from users.serializers import ProfileSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'full_name', 'major', 'gpa', 'matched', 'survey_data']
        read_only_fields = ['id', 'matched']

    def validate_gpa(self, value):
        """Validate GPA is between 0 and 4.0"""
        if not 0 <= value <= 4.0:
            raise serializers.ValidationError("GPA must be between 0 and 4.0")
        return value

    def validate_survey_data(self, value):
        """Validate survey data structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Survey data must be a JSON object")
        
        # Validate learning plan if present
        if 'learning_plan' in value:
            if not isinstance(value['learning_plan'], dict):
                raise serializers.ValidationError("Learning plan must be a JSON object")
            
            required_fields = ['objectives', 'timeline', 'resources']
            for field in required_fields:
                if field not in value['learning_plan']:
                    raise serializers.ValidationError(f"Learning plan must contain '{field}'")
        
        # Validate goals if present
        if 'goals' in value:
            if not isinstance(value['goals'], list):
                raise serializers.ValidationError("Goals must be a list")
            
            for goal in value['goals']:
                if not isinstance(goal, dict):
                    raise serializers.ValidationError("Each goal must be a JSON object")
                
                if 'description' not in goal or 'deadline' not in goal:
                    raise serializers.ValidationError("Each goal must have 'description' and 'deadline'")
        
        # Validate skills if present
        if 'skills' in value:
            if not isinstance(value['skills'], list):
                raise serializers.ValidationError("Skills must be a list")
            
            for skill in value['skills']:
                if not isinstance(skill, dict):
                    raise serializers.ValidationError("Each skill must be a JSON object")
                
                if 'name' not in skill or 'level' not in skill:
                    raise serializers.ValidationError("Each skill must have 'name' and 'level'")
                
                if skill['level'] not in ['beginner', 'intermediate', 'advanced', 'expert']:
                    raise serializers.ValidationError(f"Invalid skill level: {skill['level']}")
        
        return value 