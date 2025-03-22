from rest_framework import serializers

from .models import Match, MatchingPreference, MatchingRound, MatchingScore


class MatchingPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for matching preferences."""

    class Meta:
        model = MatchingPreference
        fields = (
            "id",
            "preference_type",
            "student",
            "organization",
            "area_of_law",
            "weight",
            "rank",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class MatchingScoreSerializer(serializers.ModelSerializer):
    """Serializer for detailed match score components."""

    class Meta:
        model = MatchingScore
        fields = (
            "id",
            "match",
            "area_of_law_score",
            "area_of_law_weight",
            "statement_score",
            "statement_weight",
            "location_score",
            "location_weight",
            "work_preference_score",
            "work_preference_weight",
            "grade_score",
            "grade_weight",
            "additional_factors",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for matches."""

    student_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    score_details = MatchingScoreSerializer(read_only=True)

    class Meta:
        model = Match
        fields = (
            "id",
            "round",
            "student",
            "student_name",
            "organization",
            "organization_name",
            "area_of_law",
            "status",
            "match_score",
            "student_rank",
            "organization_rank",
            "statement_score",
            "approved_by",
            "approved_at",
            "rejected_at",
            "notes",
            "score_details",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "approved_at", "rejected_at")

    def get_student_name(self, obj):
        return (
            f"{obj.student.first_name} {obj.student.last_name}" if obj.student else ""
        )

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else ""


class MatchingRoundSerializer(serializers.ModelSerializer):
    """Serializer for matching rounds."""

    initiated_by_name = serializers.SerializerMethodField()
    matches_count = serializers.SerializerMethodField()

    class Meta:
        model = MatchingRound
        fields = (
            "id",
            "name",
            "description",
            "status",
            "started_at",
            "completed_at",
            "initiated_by",
            "initiated_by_name",
            "algorithm_type",
            "algorithm_settings",
            "total_students",
            "matched_students",
            "total_organizations",
            "average_match_score",
            "matches_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "started_at", "completed_at")

    def get_initiated_by_name(self, obj):
        return obj.initiated_by.get_full_name() if obj.initiated_by else ""

    def get_matches_count(self, obj):
        return obj.matches.count()


class MatchingRoundDetailSerializer(MatchingRoundSerializer):
    """Detailed serializer for matching rounds including matches."""

    matches = MatchSerializer(many=True, read_only=True)

    class Meta(MatchingRoundSerializer.Meta):
        fields = MatchingRoundSerializer.Meta.fields + ("matches",)


class MatchingStatisticsSerializer(serializers.Serializer):
    """Serializer for matching statistics."""

    round = serializers.DictField(required=False)
    overall = serializers.DictField()
    matches = serializers.DictField()


class RunMatchingSerializer(serializers.Serializer):
    """Serializer for running a matching algorithm."""

    round_id = serializers.UUIDField()


class UpdateMatchStatusSerializer(serializers.Serializer):
    """Serializer for updating match status."""

    status = serializers.ChoiceField(
        choices=["PENDING", "ACCEPTED", "REJECTED", "CONFIRMED"]
    )
    notes = serializers.CharField(required=False, allow_blank=True)
