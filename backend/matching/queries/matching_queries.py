from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from matching.models import Match, MatchingRound
from matching.repositories import (MatchingPreferenceRepository,
                                   MatchingRoundRepository,
                                   MatchingScoreRepository, MatchRepository)

from backend.core.cqrs import Query, QueryHandler


@dataclass
class GetMatchingRoundQuery(Query):
    """Query to get a matching round by ID"""

    round_id: str


class GetMatchingRoundQueryHandler(
    QueryHandler[GetMatchingRoundQuery, Optional[MatchingRound]]
):
    """Handler for GetMatchingRoundQuery"""

    def __init__(self, round_repository: MatchingRoundRepository):
        self.round_repository = round_repository

    async def handle(self, query: GetMatchingRoundQuery) -> Optional[MatchingRound]:
        """Handle the get matching round query"""
        return self.round_repository.get_by_id(query.round_id)


@dataclass
class ListMatchingRoundsQuery(Query):
    """Query to list matching rounds"""

    limit: Optional[int] = None
    offset: Optional[int] = None


class ListMatchingRoundsQueryHandler(
    QueryHandler[ListMatchingRoundsQuery, List[MatchingRound]]
):
    """Handler for ListMatchingRoundsQuery"""

    def __init__(self, round_repository: MatchingRoundRepository):
        self.round_repository = round_repository

    async def handle(self, query: ListMatchingRoundsQuery) -> List[MatchingRound]:
        """Handle the list matching rounds query"""
        return self.round_repository.get_all(limit=query.limit, offset=query.offset)


@dataclass
class GetMatchQuery(Query):
    """Query to get a match by ID"""

    match_id: str


class GetMatchQueryHandler(QueryHandler[GetMatchQuery, Optional[Match]]):
    """Handler for GetMatchQuery"""

    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    async def handle(self, query: GetMatchQuery) -> Optional[Match]:
        """Handle the get match query"""
        return self.match_repository.get_by_id(query.match_id)


@dataclass
class GetMatchesForRoundQuery(Query):
    """Query to get matches for a round"""

    round_id: str
    limit: Optional[int] = None
    offset: Optional[int] = None


class GetMatchesForRoundQueryHandler(
    QueryHandler[GetMatchesForRoundQuery, List[Match]]
):
    """Handler for GetMatchesForRoundQuery"""

    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    async def handle(self, query: GetMatchesForRoundQuery) -> List[Match]:
        """Handle the get matches for round query"""
        return self.match_repository.get_round_matches(query.round_id)


@dataclass
class GetMatchesForStudentQuery(Query):
    """Query to get matches for a student"""

    student_id: str


class GetMatchesForStudentQueryHandler(
    QueryHandler[GetMatchesForStudentQuery, List[Match]]
):
    """Handler for GetMatchesForStudentQuery"""

    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    async def handle(self, query: GetMatchesForStudentQuery) -> List[Match]:
        """Handle the get matches for student query"""
        return self.match_repository.get_student_matches(query.student_id)


@dataclass
class GetMatchesForOrganizationQuery(Query):
    """Query to get matches for an organization"""

    organization_id: str


class GetMatchesForOrganizationQueryHandler(
    QueryHandler[GetMatchesForOrganizationQuery, List[Match]]
):
    """Handler for GetMatchesForOrganizationQuery"""

    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    async def handle(self, query: GetMatchesForOrganizationQuery) -> List[Match]:
        """Handle the get matches for organization query"""
        return self.match_repository.get_organization_matches(query.organization_id)


@dataclass
class GetMatchingStatisticsQuery(Query):
    """Query to get matching statistics"""

    round_id: Optional[str] = None


class GetMatchingStatisticsQueryHandler(
    QueryHandler[GetMatchingStatisticsQuery, Dict[str, Any]]
):
    """Handler for GetMatchingStatisticsQuery"""

    def __init__(
        self,
        round_repository: MatchingRoundRepository,
        match_repository: MatchRepository,
    ):
        self.round_repository = round_repository
        self.match_repository = match_repository

    async def handle(self, query: GetMatchingStatisticsQuery) -> Dict[str, Any]:
        """Handle the get matching statistics query"""
        round_stats = None
        if query.round_id:
            round = self.round_repository.get_by_id(query.round_id)
            if round:
                round_stats = {
                    "id": round.id,
                    "name": round.name,
                    "status": round.status,
                    "total_students": round.total_students,
                    "matched_students": round.matched_students,
                    "match_percentage": (
                        (round.matched_students / round.total_students * 100)
                        if round.total_students
                        else 0
                    ),
                    "average_score": round.average_match_score or 0,
                }

        # Get overall statistics
        overall_stats = self.round_repository.get_statistics()

        # Get match statistics
        match_stats = self.match_repository.get_match_statistics(query.round_id)

        return {
            "round": round_stats,
            "overall": overall_stats,
            "matches": match_stats,
        }
