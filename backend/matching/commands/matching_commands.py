from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.db import transaction
from matching.algorithms import get_algorithm
from matching.models import Match, MatchingRound
from matching.repositories import (MatchingPreferenceRepository,
                                   MatchingRoundRepository,
                                   MatchingScoreRepository, MatchRepository)
from organizations.repositories import OrganizationRepository
from statements.repositories import GradeRepository, StatementRepository
from students.repositories import StudentRepository
from ..services import call_matching_microservice

from backend.core.cqrs import Command, CommandHandler


def run_matching_command(student_ids: list[int], round_id: int) -> dict:
    result = call_matching_microservice(student_ids, round_id)
    return result


@dataclass
class CreateMatchingRoundCommand(Command):
    """Command to create a matching round"""

    name: str
    description: Optional[str] = None
    algorithm_type: str = "weighted_preference"
    settings: Optional[Dict[str, Any]] = None


class CreateMatchingRoundCommandHandler(CommandHandler[CreateMatchingRoundCommand]):
    """Handler for CreateMatchingRoundCommand"""

    def __init__(self, round_repository: MatchingRoundRepository):
        self.round_repository = round_repository

    async def handle(self, command: CreateMatchingRoundCommand) -> MatchingRound:
        """Handle the create matching round command"""
        return self.round_repository.create_new_round(
            name=command.name,
            algorithm_type=command.algorithm_type,
            settings=command.settings or {},
        )


@dataclass
class RunMatchingCommand(Command):
    """Command to run a matching round"""

    round_id: str
    user_id: Optional[str] = None


class RunMatchingCommandHandler(CommandHandler[RunMatchingCommand]):
    """Handler for RunMatchingCommand"""

    def __init__(
        self,
        round_repository: MatchingRoundRepository,
        match_repository: MatchRepository,
        preference_repository: MatchingPreferenceRepository,
        score_repository: MatchingScoreRepository,
        student_repository: StudentRepository,
        org_repository: OrganizationRepository,
        statement_repository: StatementRepository,
        grade_repository: GradeRepository,
    ):
        self.round_repository = round_repository
        self.match_repository = match_repository
        self.preference_repository = preference_repository
        self.score_repository = score_repository
        self.student_repository = student_repository
        self.org_repository = org_repository
        self.statement_repository = statement_repository
        self.grade_repository = grade_repository

    @transaction.atomic
    async def handle(self, command: RunMatchingCommand) -> MatchingRound:
        """Handle the run matching command"""
        # Get the matching round
        round = self.round_repository.get_by_id(command.round_id)
        if not round:
            raise ValueError(f"Matching round with ID {command.round_id} not found")

        # Check if round is already completed
        if round.status == "COMPLETED":
            return round

        # Mark round as in progress
        round.start(command.user_id)

        try:
            # Get eligible students and organizations
            students = self.student_repository.get_all_active()
            organizations = self.org_repository.get_all_active()

            # Count totals for tracking
            round.total_students = len(students)
            round.total_organizations = len(organizations)
            round.save(update_fields=["total_students", "total_organizations"])

            # Get all preferences
            all_preferences = self.preference_repository.get_all()

            # Get statements and grades if needed
            statements = self.statement_repository.get_all_with_grades()
            grades = self.grade_repository.get_all_for_students(
                [s.id for s in students]
            )

            # Use factory to get the right algorithm
            algorithm = get_algorithm(round.algorithm_type, round.algorithm_settings)

            # Prepare and run the algorithm
            algorithm.prepare(
                students, organizations, all_preferences, grades, statements
            )
            matches = algorithm.execute()

            # Get summary statistics
            summary = algorithm.get_results_summary()

            # Save matches to database
            saved_matches = []
            for match_data in matches:
                match = self.match_repository.create(
                    round=round,
                    student_id=match_data["student_id"],
                    organization_id=match_data["organization_id"],
                    area_of_law=match_data["area_of_law"],
                    match_score=match_data["match_score"],
                    student_rank=match_data.get("student_rank"),
                    organization_rank=match_data.get("organization_rank"),
                )
                saved_matches.append(match)

                # Save detailed score components if available
                if "components" in match_data:
                    self.score_repository.create_score(match, match_data["components"])

            # Mark round as completed
            round.complete(
                matched_count=len(saved_matches), avg_score=summary.get("average_score")
            )

            return round

        except Exception as e:
            round.fail()
            raise


@dataclass
class UpdateMatchStatusCommand(Command):
    """Command to update a match status"""

    match_id: str
    status: str
    user_id: Optional[str] = None
    notes: Optional[str] = None


class UpdateMatchStatusCommandHandler(CommandHandler[UpdateMatchStatusCommand]):
    """Handler for UpdateMatchStatusCommand"""

    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    async def handle(self, command: UpdateMatchStatusCommand) -> Match:
        """Handle the update match status command"""
        match = self.match_repository.get_by_id(command.match_id)
        if not match:
            raise ValueError(f"Match with ID {command.match_id} not found")

        if command.status == "ACCEPTED":
            match.approve(command.user_id)
        elif command.status == "REJECTED":
            match.reject(command.user_id, command.notes)
        elif command.status == "CONFIRMED":
            match.confirm()
        else:
            match.status = command.status
            match.save(update_fields=["status", "updated_at"])

        return match
