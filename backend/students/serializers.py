from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (AreaOfLaw, SelfProposedExternship, Statement, Student,
                     StudentAreaRanking, StudentGrade)


class AreaOfLawSerializer(serializers.ModelSerializer):
    """Serializer for AreaOfLaw entities."""

    class Meta:
        model = AreaOfLaw
        fields = ("id", "name", "description")


class StudentAreaRankingSerializer(serializers.ModelSerializer):
    """Serializer for StudentAreaRanking entities."""

    area_name = serializers.CharField(source="area.name", read_only=True)

    class Meta:
        model = StudentAreaRanking
        fields = ("id", "area", "area_name", "rank", "comments")


class StatementSerializer(serializers.ModelSerializer):
    """Serializer for Statement entities."""

    area_name = serializers.CharField(source="area_of_law.name", read_only=True)
    graded_by_name = serializers.CharField(
        source="graded_by.get_full_name", read_only=True
    )

    class Meta:
        model = Statement
        fields = (
            "id",
            "student",
            "area_of_law",
            "area_name",
            "content",
            "statement_grade",
            "graded_by",
            "graded_by_name",
            "graded_at",
        )


class StudentGradeSerializer(serializers.ModelSerializer):
    """Serializer for StudentGrade entities."""

    class Meta:
        model = StudentGrade
        fields = (
            "id",
            "student",
            "constitutional_law",
            "contracts",
            "criminal_law",
            "property_law",
            "torts",
            "lrw_case_brief",
            "lrw_multiple_case",
            "lrw_short_memo",
            "grade_pdf",
        )


class SelfProposedExternshipSerializer(serializers.ModelSerializer):
    """Serializer for SelfProposedExternship entities."""

    class Meta:
        model = SelfProposedExternship
        fields = (
            "id",
            "student",
            "organization",
            "supervisor",
            "supervisor_email",
            "address",
            "website",
            "description",
        )


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student entities."""

    profile_completion = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = (
            "id",
            "student_id",
            "given_names",
            "last_name",
            "full_name",
            "email",
            "backup_email",
            "program",
            "location_preferences",
            "work_preferences",
            "is_matched",
            "needs_approval",
            "is_active",
            "last_active",
            "profile_completion",
            "created_at",
            "updated_at",
        )


class StudentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Student entities including related data."""

    profile_completion = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    grades = StudentGradeSerializer(read_only=True)
    statements = StatementSerializer(many=True, read_only=True)
    area_rankings = StudentAreaRankingSerializer(many=True, read_only=True)
    self_proposed = SelfProposedExternshipSerializer(read_only=True)

    class Meta:
        model = Student
        fields = (
            "id",
            "student_id",
            "given_names",
            "last_name",
            "full_name",
            "email",
            "backup_email",
            "program",
            "location_preferences",
            "work_preferences",
            "is_matched",
            "needs_approval",
            "is_active",
            "last_active",
            "profile_completion",
            "created_at",
            "updated_at",
            "grades",
            "statements",
            "area_rankings",
            "self_proposed",
        )


class ImportCSVSerializer(serializers.Serializer):
    """Serializer for handling CSV file uploads."""

    csv_file = serializers.FileField()

    def validate_csv_file(self, value):
        """Validate that the file is a CSV."""
        if not value.name.endswith(".csv"):
            raise serializers.ValidationError("File must be a CSV document")
        return value


class ImportPDFSerializer(serializers.Serializer):
    """Serializer for handling PDF grade uploads."""

    student_id = serializers.CharField(max_length=50)
    grades_pdf = serializers.FileField()

    def validate_grades_pdf(self, value):
        """Validate that the file is a PDF."""
        if not value.name.endswith(".pdf"):
            raise serializers.ValidationError("File must be a PDF document")
        return value
