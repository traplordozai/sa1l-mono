from core.repositories import BaseRepository
from django.db.models import Avg, Count, F, Q, Sum
from organizations.models import Organization
from students.models import Student

from .models import Match, MatchingPreference, MatchingRound, MatchingScore


class MatchingRoundRepository(BaseRepository):
    """Repository for accessing matching round data."""

    model = MatchingRound

    def create_new_round(
        self, name, algorithm_type="weighted_preference", settings=None
    ):
        """Create a new matching round with specified settings"""
        return self.model.objects.create(
            name=name, algorithm_type=algorithm_type, algorithm_settings=settings or {}
        )

    def get_recent_rounds(self, limit=5):
        """Get the most recent matching rounds"""
        return self.model.objects.all()[:limit]

    def get_statistics(self):
        """Get summary statistics of all matching rounds"""
        return {
            "total_rounds": self.model.objects.count(),
            "completed_rounds": self.model.objects.filter(status="COMPLETED").count(),
            "total_matches": Match.objects.count(),
            "confirmed_matches": Match.objects.filter(status="CONFIRMED").count(),
            "average_score": Match.objects.aggregate(avg_score=Avg("match_score"))[
                "avg_score"
            ]
            or 0,
        }


class MatchRepository(BaseRepository):
    """Repository for accessing match data."""

    model = Match

    def get_student_matches(self, student_id):
        """Get all matches for a specific student"""
        return self.model.objects.filter(student_id=student_id)

    def get_organization_matches(self, organization_id):
        """Get all matches for a specific organization"""
        return self.model.objects.filter(organization_id=organization_id)

    def get_round_matches(self, round_id):
        """Get all matches for a specific round"""
        return self.model.objects.filter(round_id=round_id)

    def bulk_create_matches(self, matches_data):
        """Create multiple matches in a single operation"""
        matches = [self.model(**data) for data in matches_data]
        return self.model.objects.bulk_create(matches)

    def get_match_statistics(self, round_id=None):
        """Get statistics about matches"""
        query = self.model.objects.all()
        if round_id:
            query = query.filter(round_id=round_id)

        return {
            "total": query.count(),
            "by_status": dict(
                query.values("status")
                .annotate(count=Count("id"))
                .values_list("status", "count")
            ),
            "avg_score": query.aggregate(avg=Avg("match_score"))["avg"] or 0,
            "by_area": dict(
                query.values("area_of_law")
                .annotate(count=Count("id"))
                .values_list("area_of_law", "count")
            ),
        }


class MatchingPreferenceRepository(BaseRepository):
    """Repository for accessing matching preference data."""

    model = MatchingPreference

    def get_student_preferences(self, student_id):
        """Get all preferences for a specific student"""
        return self.model.objects.filter(
            preference_type="STUDENT", student_id=student_id
        ).order_by("rank")

    def get_organization_preferences(self, organization_id):
        """Get all preferences for a specific organization"""
        return self.model.objects.filter(
            preference_type="ORGANIZATION", organization_id=organization_id
        ).order_by("weight")

    def get_preferences_by_area(self, area_of_law):
        """Get all preferences for a specific area of law"""
        return self.model.objects.filter(area_of_law=area_of_law)


class MatchingScoreRepository(BaseRepository):
    """Repository for accessing match score data."""

    model = MatchingScore

    def create_score(self, match, score_details):
        """Create a new score detail record for a match"""
        return self.model.objects.create(match=match, **score_details)

    def get_score_details(self, match_id):
        """Get detailed score breakdown for a match"""
        return self.model.objects.filter(match_id=match_id).first()
