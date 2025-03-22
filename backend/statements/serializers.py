# backend/statements/serializers.py
from rest_framework import serializers

from .models import (AreaOfLaw, GradeImport, GradingRubric, RubricCriterion,
                     Statement)


class AreaOfLawSerializer(serializers.ModelSerializer):
    """
    Serializer for area of law data.
    """

    statement_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = AreaOfLaw
        fields = ["id", "name", "description", "statement_count"]


class RubricCriterionSerializer(serializers.ModelSerializer):
    """
    Serializer for rubric criterion data.
    """

    class Meta:
        model = RubricCriterion
        fields = ["id", "name", "description", "max_points"]


class GradingRubricSerializer(serializers.ModelSerializer):
    """
    Serializer for grading rubric data.
    """

    criteria = RubricCriterionSerializer(many=True, read_only=True)
    area_of_law_name = serializers.CharField(source="area_of_law.name", read_only=True)

    class Meta:
        model = GradingRubric
        fields = [
            "id",
            "name",
            "description",
            "area_of_law",
            "area_of_law_name",
            "max_points",
            "is_active",
            "criteria",
        ]


class StatementSerializer(serializers.ModelSerializer):
    """
    Serializer for statement data.
    """

    student_name = serializers.CharField(source="student.full_name", read_only=True)
    area_of_law_name = serializers.CharField(source="area_of_law.name", read_only=True)
    graded_by_name = serializers.CharField(
        source="graded_by.get_full_name", read_only=True
    )
    is_graded = serializers.BooleanField(read_only=True)

    class Meta:
        model = Statement
        fields = [
            "id",
            "student",
            "student_name",
            "area_of_law",
            "area_of_law_name",
            "content",
            "grade",
            "graded_by",
            "graded_by_name",
            "graded_at",
            "is_graded",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["graded_by", "graded_at", "created_at", "updated_at"]


class StatementCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new statement.
    """

    class Meta:
        model = Statement
        fields = ["student", "area_of_law", "content"]


class StatementUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing statement.
    """

    class Meta:
        model = Statement
        fields = ["content"]


class GradeStatementSerializer(serializers.Serializer):
    """
    Serializer for the grading action.
    """

    grade = serializers.IntegerField(min_value=0, max_value=25)
    comments = serializers.CharField(required=False, allow_blank=True)


class GradeImportSerializer(serializers.ModelSerializer):
    """
    Serializer for grade import records.
    """

    imported_by_name = serializers.CharField(
        source="imported_by.get_full_name", read_only=True
    )

    class Meta:
        model = GradeImport
        fields = [
            "id",
            "imported_by",
            "imported_by_name",
            "file_name",
            "import_date",
            "success_count",
            "error_count",
            "errors",
        ]
        read_only_fields = [
            "imported_by",
            "import_date",
            "success_count",
            "error_count",
            "errors",
        ]


class GradingStatisticsSerializer(serializers.Serializer):
    """
    Serializer for grading statistics data.
    """

    total_statements = serializers.IntegerField()
    graded_statements = serializers.IntegerField()
    ungraded_statements = serializers.IntegerField()
    completion_percentage = serializers.FloatField()
    area_statistics = serializers.ListField(child=serializers.DictField())
