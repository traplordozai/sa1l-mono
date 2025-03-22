from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.events import (StudentCreatedEvent, StudentMatchedEvent,
                         StudentUpdatedEvent)
from core.handlers import EventBus
from django.db import transaction
from django.utils import timezone
from students.models import Student
from students.repositories import (AreaOfLawRepository,
                                   SelfProposedExternshipRepository,
                                   StatementRepository,
                                   StudentAreaRankingRepository,
                                   StudentGradeRepository, StudentRepository)

from backend.core.cqrs import Command, CommandHandler


@dataclass
class CreateStudentCommand(Command):
    """Command to create a new student"""

    data: Dict[str, Any]


class CreateStudentCommandHandler(CommandHandler[CreateStudentCommand]):
    """Handler for CreateStudentCommand"""

    def __init__(
        self,
        student_repository: StudentRepository,
        area_repository: AreaOfLawRepository,
        ranking_repository: StudentAreaRankingRepository,
        statement_repository: StatementRepository,
        grade_repository: StudentGradeRepository,
        externship_repository: SelfProposedExternshipRepository,
        event_bus: EventBus,
    ):
        self.student_repository = student_repository
        self.area_repository = area_repository
        self.ranking_repository = ranking_repository
        self.statement_repository = statement_repository
        self.grade_repository = grade_repository
        self.externship_repository = externship_repository
        self.event_bus = event_bus

    @transaction.atomic
    async def handle(self, command: CreateStudentCommand) -> Student:
        """Handle the create student command"""
        data = command.data.copy()

        # Extract related data
        area_rankings = data.pop("area_rankings", [])
        statements = data.pop("statements", [])
        grades_data = data.pop("grades", None)
        self_proposed_data = data.pop("self_proposed", None)

        # Create student
        student = self.student_repository.create(**data)

        # Create area rankings if provided
        for ranking in area_rankings:
            area_id = ranking.get("area")
            rank = ranking.get("rank")
            comments = ranking.get("comments", "")

            area = self.area_repository.get_by_id(area_id)
            if area and rank:
                self.ranking_repository.create(
                    student=student, area=area, rank=rank, comments=comments
                )

        # Create statements if provided
        for statement in statements:
            area_id = statement.get("area_of_law")
            content = statement.get("content", "")

            area = self.area_repository.get_by_id(area_id)
            if area and content:
                self.statement_repository.create(
                    student=student, area_of_law=area, content=content
                )

        # Create grades if provided
        if grades_data:
            self.grade_repository.create(student=student, **grades_data)

        # Create self-proposed externship if provided
        if self_proposed_data:
            self.externship_repository.create(student=student, **self_proposed_data)

        # Publish event
        event = StudentCreatedEvent(
            aggregate_id=str(student.id),
            data={
                "student_id": student.student_id,
                "email": student.email,
                "first_name": student.first_name,
                "last_name": student.last_name,
            },
        )
        self.event_bus.publish(event)

        return student


@dataclass
class UpdateStudentCommand(Command):
    """Command to update an existing student"""

    id: str
    data: Dict[str, Any]


class UpdateStudentCommandHandler(CommandHandler[UpdateStudentCommand]):
    """Handler for UpdateStudentCommand"""

    def __init__(
        self,
        student_repository: StudentRepository,
        area_repository: AreaOfLawRepository,
        ranking_repository: StudentAreaRankingRepository,
        statement_repository: StatementRepository,
        grade_repository: StudentGradeRepository,
        externship_repository: SelfProposedExternshipRepository,
        event_bus: EventBus,
    ):
        self.student_repository = student_repository
        self.area_repository = area_repository
        self.ranking_repository = ranking_repository
        self.statement_repository = statement_repository
        self.grade_repository = grade_repository
        self.externship_repository = externship_repository
        self.event_bus = event_bus

    @transaction.atomic
    async def handle(self, command: UpdateStudentCommand) -> Optional[Student]:
        """Handle the update student command"""
        data = command.data.copy()
        student = self.student_repository.get_by_id(command.id)
        if not student:
            return None

        # Extract related data
        area_rankings = data.pop("area_rankings", None)
        statements = data.pop("statements", None)
        grades_data = data.pop("grades", None)
        self_proposed_data = data.pop("self_proposed", None)

        # Update student
        student = self.student_repository.update(student, **data)

        # Update area rankings if provided
        if area_rankings is not None:
            # Remove existing rankings and create new ones
            existing_rankings = self.ranking_repository.get_by_student(student)
            for ranking in existing_rankings:
                self.ranking_repository.delete(ranking)

            for ranking in area_rankings:
                area_id = ranking.get("area")
                rank = ranking.get("rank")
                comments = ranking.get("comments", "")

                area = self.area_repository.get_by_id(area_id)
                if area and rank:
                    self.ranking_repository.create(
                        student=student, area=area, rank=rank, comments=comments
                    )

        # Update statements if provided
        if statements is not None:
            # Update existing statements and create new ones as needed
            existing_statements = {
                s.area_of_law.id: s
                for s in self.statement_repository.get_by_student(student)
            }

            for statement_data in statements:
                area_id = statement_data.get("area_of_law")
                content = statement_data.get("content", "")

                if area_id in existing_statements:
                    # Update existing statement
                    statement = existing_statements[area_id]
                    self.statement_repository.update(statement, content=content)
                else:
                    # Create new statement
                    area = self.area_repository.get_by_id(area_id)
                    if area and content:
                        self.statement_repository.create(
                            student=student, area_of_law=area, content=content
                        )

        # Update grades if provided
        if grades_data:
            existing_grades = self.grade_repository.get_by_student(student)
            if existing_grades:
                self.grade_repository.update(existing_grades, **grades_data)
            else:
                self.grade_repository.create(student=student, **grades_data)

        # Update self-proposed externship if provided
        if self_proposed_data:
            existing_externship = self.externship_repository.get_by_student(student)
            if existing_externship:
                self.externship_repository.update(
                    existing_externship, **self_proposed_data
                )
            else:
                self.externship_repository.create(student=student, **self_proposed_data)

        # Publish event
        event = StudentUpdatedEvent(
            aggregate_id=str(student.id),
            data={
                "student_id": student.student_id,
                "updated_fields": list(command.data.keys()),
            },
        )
        self.event_bus.publish(event)

        return student


@dataclass
class DeleteStudentCommand(Command):
    """Command to delete a student"""

    id: str


class DeleteStudentCommandHandler(CommandHandler[DeleteStudentCommand]):
    """Handler for DeleteStudentCommand"""

    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def handle(self, command: DeleteStudentCommand) -> bool:
        """Handle the delete student command"""
        student = self.student_repository.get_by_id(command.id)
        if not student:
            return False

        # Soft delete the student
        self.student_repository.soft_delete(student)
        return True


@dataclass
class MatchStudentWithOrganizationCommand(Command):
    """Command to match a student with an organization"""

    student_id: str
    organization_id: str
    match_data: Dict[str, Any]


class MatchStudentWithOrganizationCommandHandler(
    CommandHandler[MatchStudentWithOrganizationCommand]
):
    """Handler for MatchStudentWithOrganizationCommand"""

    def __init__(self, student_repository: StudentRepository, event_bus: EventBus):
        self.student_repository = student_repository
        self.event_bus = event_bus

    async def handle(self, command: MatchStudentWithOrganizationCommand) -> Student:
        """Handle the match student command"""
        student = self.student_repository.get_by_id(command.student_id)
        student.is_matched = True
        student.last_active = timezone.now()
        student = self.student_repository.save(student)

        # Publish event
        event = StudentMatchedEvent(
            aggregate_id=str(student.id),
            data={
                "student_id": student.student_id,
                "match": {
                    "organization_id": command.organization_id,
                    "match_date": timezone.now().isoformat(),
                    **command.match_data,
                },
            },
        )
        self.event_bus.publish(event)

        return student
