from rest_framework import serializers

from .models import ImportDetail, ImportLog, ImportStatus, ImportType


class ImportDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for ImportDetail records
    """

    class Meta:
        model = ImportDetail
        fields = [
            "id",
            "entity_type",
            "entity_id",
            "row_number",
            "status",
            "message",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Include a preview of the original data (limited to avoid large responses)
        if instance.original_data:
            try:
                keys = list(instance.original_data.keys())[:5]  # First 5 keys
                rep["data_preview"] = {k: instance.original_data[k] for k in keys}
            except (AttributeError, TypeError):
                rep["data_preview"] = "Data preview not available"
        else:
            rep["data_preview"] = None

        return rep


class ImportLogSerializer(serializers.ModelSerializer):
    """
    Serializer for ImportLog records
    """

    imported_by_name = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    import_type_display = serializers.CharField(source="get_import_type_display")
    status_display = serializers.CharField(source="get_status_display")

    class Meta:
        model = ImportLog
        fields = [
            "id",
            "import_type",
            "import_type_display",
            "file_name",
            "original_file_name",
            "file_size",
            "status",
            "status_display",
            "processed_count",
            "success_count",
            "error_count",
            "warnings_count",
            "started_at",
            "completed_at",
            "execution_time",
            "imported_by",
            "imported_by_name",
            "task_id",
            "created_at",
            "updated_at",
            "success_rate",
            "duration",
        ]

    def get_imported_by_name(self, obj):
        if obj.imported_by:
            return (
                f"{obj.imported_by.first_name} {obj.imported_by.last_name}".strip()
                or obj.imported_by.username
            )
        return "System"

    def get_success_rate(self, obj):
        return obj.success_rate

    def get_duration(self, obj):
        """
        Format execution time as human-readable duration
        """
        if not obj.execution_time:
            return None

        seconds = obj.execution_time

        if seconds < 60:
            return f"{seconds} seconds"

        minutes = seconds // 60
        remaining_seconds = seconds % 60

        if minutes < 60:
            return f"{minutes} min {remaining_seconds} sec"

        hours = minutes // 60
        remaining_minutes = minutes % 60

        return f"{hours} hr {remaining_minutes} min"
