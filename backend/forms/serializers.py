from rest_framework import serializers
from .models import DynamicForm, DynamicSubmission

class DynamicFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicForm
        fields = ['id', 'name', 'schema']
        read_only_fields = ['id']

    def validate_schema(self, value):
        """Validate the JSON schema structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Schema must be a JSON object")
        
        if 'fields' not in value:
            raise serializers.ValidationError("Schema must contain a 'fields' array")
        
        if not isinstance(value['fields'], list):
            raise serializers.ValidationError("'fields' must be an array")
        
        for field in value['fields']:
            if not isinstance(field, dict):
                raise serializers.ValidationError("Each field must be an object")
            
            required_keys = ['id', 'label', 'type']
            for key in required_keys:
                if key not in field:
                    raise serializers.ValidationError(f"Each field must contain '{key}'")
            
            if field['type'] not in ['text', 'number', 'email', 'date', 'select', 'checkbox']:
                raise serializers.ValidationError(f"Invalid field type: {field['type']}")
        
        return value

class DynamicSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicSubmission
        fields = ['id', 'form', 'user', 'answers', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']

    def validate_answers(self, value):
        """Validate the submission answers against the form schema"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Answers must be a JSON object")
        
        form = self.context.get('form')
        if not form:
            raise serializers.ValidationError("Form context is required")
        
        schema = form.schema
        field_ids = {field['id'] for field in schema['fields']}
        
        for field_id, answer in value.items():
            if field_id not in field_ids:
                raise serializers.ValidationError(f"Unknown field: {field_id}")
            
            field = next(f for f in schema['fields'] if f['id'] == field_id)
            if field.get('required', False) and not answer:
                raise serializers.ValidationError(f"Field '{field_id}' is required")
        
        return value 