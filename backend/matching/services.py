import logging
from typing import Any, Dict, List, Optional
import requests

from core.handlers import EventBus
from django.db import transaction
from django.utils import timezone
from organizations.repositories import OrganizationRepository
from statements.repositories import GradeRepository, StatementRepository
from students.repositories import StudentRepository

from backend.core.cqrs import CommandDispatcher, QueryDispatcher

from .commands.matching_commands import (CreateMatchingRoundCommand,
                                         RunMatchingCommand,
                                         UpdateMatchStatusCommand)
from .models import Match, MatchingRound
from .queries.matching_queries import (GetMatchesForOrganizationQuery,
                                       GetMatchesForRoundQuery,
                                       GetMatchesForStudentQuery,
                                       GetMatchingRoundQuery,
                                       GetMatchingStatisticsQuery,
                                       GetMatchQuery, ListMatchingRoundsQuery)
from .repositories import (MatchingPreferenceRepository,
                           MatchingRoundRepository, MatchingScoreRepository,
                           MatchRepository)

logger = logging.getLogger(__name__)


def call_matching_microservice(student_ids: list[int], round_id: int) -> dict:
    url = "http://localhost:9000/match"
    payload = {
        "student_ids": student_ids,
        "round_id": round_id
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


class MatchingService:
    """Service for managing the matching process."""

    def __init__(self):
        # Repositories
        self.round_repo = MatchingRoundRepository()
        self.match_repo = MatchRepository()
        self.preference_repo = MatchingPreferenceRepository()
        self.score_repo = MatchingScoreRepository()
        self.student_repo = StudentRepository()
        self.org_repo = OrganizationRepository()
        self.statement_repo = StatementRepository()
        self.grade_repo = GradeRepository()
        self.event_bus = EventBus()

        # Command dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.command_dispatcher.register(
            CreateMatchingRoundCommand,
            CreateMatchingRoundCommandHandler(self.round_repo),
        )
        self.command_dispatcher.register(
            RunMatchingCommand,
            RunMatchingCommandHandler(
                self.round_repo,
                self.match_repo,
                self.preference_repo,
                self.score_repo,
                self.student_repo,
                self.org_repo,
                self.statement_repo,
                self.grade_repo,
            ),
        )
        self.command_dispatcher.register(
            UpdateMatchStatusCommand, UpdateMatchStatusCommandHandler(self.match_repo)
        )

        # Query dispatcher
        self.query_dispatcher = QueryDispatcher()
        self.query_dispatcher.register(
            GetMatchingRoundQuery, GetMatchingRoundQueryHandler(self.round_repo)
        )
        self.query_dispatcher.register(
            ListMatchingRoundsQuery, ListMatchingRoundsQueryHandler(self.round_repo)
        )
        self.query_dispatcher.register(
            GetMatchQuery, GetMatchQueryHandler(self.match_repo)
        )
        self.query_dispatcher.register(
            GetMatchesForRoundQuery, GetMatchesForRoundQueryHandler(self.match_repo)
        )
        self.query_dispatcher.register(
            GetMatchesForStudentQuery, GetMatchesForStudentQueryHandler(self.match_repo)
        )
        self.query_dispatcher.register(
            GetMatchesForOrganizationQuery,
            GetMatchesForOrganizationQueryHandler(self.match_repo),
        )
        self.query_dispatcher.register(
            GetMatchingStatisticsQuery,
            GetMatchingStatisticsQueryHandler(self.round_repo, self.match_repo),
        )

    async def create_matching_round(
        self,
        name,
        description=None,
        algorithm_type="weighted_preference",
        settings=None,
    ):
        """Create a new matching round"""
        command = CreateMatchingRoundCommand(
            name=name,
            description=description,
            algorithm_type=algorithm_type,
            settings=settings,
        )
        return await self.command_dispatcher.dispatch(command)

    async def get_round(self, round_id):
        """Get a specific matching round by ID"""
        query = GetMatchingRoundQuery(round_id=round_id)
        return await self.query_dispatcher.dispatch(query)

    async def list_rounds(self, limit=None, offset=None):
        """List matching rounds with optional pagination"""
        query = ListMatchingRoundsQuery(limit=limit, offset=offset)
        return await self.query_dispatcher.dispatch(query)

    async def run_matching(self, round_id, user=None):
        """Run the matching algorithm for a specific round"""
        command = RunMatchingCommand(
            round_id=round_id, user_id=user.id if user else None
        )
        return await self.command_dispatcher.dispatch(command)

    async def get_match(self, match_id):
        """Get a specific match by ID"""
        query = GetMatchQuery(match_id=match_id)
        return await self.query_dispatcher.dispatch(query)

    async def update_match_status(self, match_id, status, user=None, notes=None):
        """Update the status of a match"""
        command = UpdateMatchStatusCommand(
            match_id=match_id,
            status=status,
            user_id=user.id if user else None,
            notes=notes,
        )
        return await self.command_dispatcher.dispatch(command)

    async def get_matches_for_round(self, round_id, limit=None, offset=None):
        """Get all matches for a specific round"""
        query = GetMatchesForRoundQuery(round_id=round_id, limit=limit, offset=offset)
        return await self.query_dispatcher.dispatch(query)

    async def get_matches_for_student(self, student_id):
        """Get all matches for a specific student"""
        query = GetMatchesForStudentQuery(student_id=student_id)
        return await self.query_dispatcher.dispatch(query)

    async def get_matches_for_organization(self, organization_id):
        """Get all matches for a specific organization"""
        query = GetMatchesForOrganizationQuery(organization_id=organization_id)
        return await self.query_dispatcher.dispatch(query)

    async def get_matching_statistics(self, round_id=None):
        """Get statistics about the matching process"""
        query = GetMatchingStatisticsQuery(round_id=round_id)
        return await self.query_dispatcher.dispatch(query)
