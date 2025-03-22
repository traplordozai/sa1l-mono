from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from core.events import StatementGradedEvent, StatementSubmittedEvent
from core.handlers import EventBus
from django.db import transaction
from statements.models import AreaOfLaw, Statement
from statements.repositories import (AreaOfLawRepository,
                                     GradeImportRepository,
                                     GradingRubricRepository,
                                     StatementRepository)
from students.repositories import StudentRepository

from backend.core.cqrs import Command, CommandHandler


@dataclass
class CreateStatementCommand(Command):
    """Command to create a statement"""

    student_id: str
    area_id: str
    content: str


class CreateStatementCommandHandler(CommandHandler[CreateStatementCommand]):
    """Handler for CreateStatementCommand"""

    def __init__(
        self,
        statement_repository: StatementRepository,
        student_repository: StudentRepository,
        area_repository: AreaOfLawRepository,
        event_bus: EventBus,
    ):
        self.statement_repository = statement_repository
        self.student_repository = student_repository
        self.area_repository = area_repository
        self.event_bus = event_bus

    async def handle(self, command: CreateStatementCommand) -> Statement:
        """Handle the create statement command"""
        # Validate student exists
        student = self.student_repository.get_by_id(command.student_id)
        if not student:
            raise ValueError(f"Student with ID {command.student_id} not found")

        # Validate area of law exists
        area = self.area_repository.get_by_id(command.area_id)
        if not area:
            raise ValueError(f"Area of law with ID {command.area_id} not found")

        # Check if student already has a statement for this area
        existing = self.statement_repository.model.objects.filter(
            student_id=command.student_id, area_of_law_id=command.area_id
        ).first()

        if existing:
            raise ValueError(f"Student already has a statement for {area.name}")

        # Create the statement
        statement = self.statement_repository.create(
            student_id=command.student_id,
            area_of_law_id=command.area_id,
            content=command.content,
        )

        # Publish event
        event = StatementSubmittedEvent(
            aggregate_id=str(statement.id),
            data={
                "student_id": command.student_id,
                "area_id": command.area_id,
                "area_name": area.name,
            },
        )
        self.event_bus.publish(event)

        return statement


@dataclass
class UpdateStatementCommand(Command):
    """Command to update a statement"""

    statement_id: str
    content: str


class UpdateStatementCommandHandler(CommandHandler[UpdateStatementCommand]):
    """Handler for UpdateStatementCommand"""

    def __init__(self, statement_repository: StatementRepository):
        self.statement_repository = statement_repository

    async def handle(self, command: UpdateStatementCommand) -> Statement:
        """Handle the update statement command"""
        statement = self.statement_repository.get_by_id(command.statement_id)
        if not statement:
            raise ValueError(f"Statement with ID {command.statement_id} not found")

        # Cannot update graded statements
        if statement.is_graded:
            raise ValueError("Cannot update a statement that has already been graded")

        statement.content = command.content
        statement.save()
        return statement


@dataclass
class DeleteStatementCommand(Command):
    """Command to delete a statement"""

    statement_id: str


class DeleteStatementCommandHandler(CommandHandler[DeleteStatementCommand]):
    """Handler for DeleteStatementCommand"""

    def __init__(self, statement_repository: StatementRepository):
        self.statement_repository = statement_repository

    async def handle(self, command: DeleteStatementCommand) -> None:
        """Handle the delete statement command"""
        statement = self.statement_repository.get_by_id(command.statement_id)
        if not statement:
            raise ValueError(f"Statement with ID {command.statement_id} not found")

        # Cannot delete graded statements
        if statement.is_graded:
            raise ValueError("Cannot delete a statement that has already been graded")

        statement.delete()


@dataclass
class GradeStatementCommand(Command):
    """Command to grade a statement"""

    statement_id: str
    grade: int
    grader_id: str
    comments: str = ""


class GradeStatementCommandHandler(CommandHandler[GradeStatementCommand]):
    """Handler for GradeStatementCommand"""

    def __init__(self, statement_repository: StatementRepository, event_bus: EventBus):
        self.statement_repository = statement_repository
        self.event_bus = event_bus

    @transaction.atomic
    async def handle(self, command: GradeStatementCommand) -> Statement:
        """Handle the grade statement command"""
        statement = self.statement_repository.get_by_id(command.statement_id)
        if not statement:
            raise ValueError(f"Statement with ID {command.statement_id} not found")

        # Check if already graded
        if statement.is_graded:
            raise ValueError(
                f"Statement has already been graded by {statement.graded_by}"
            )

        # Validate the grade is within range (0-25)
        if command.grade < 0 or command.grade > 25:
            raise ValueError("Grade must be between 0 and 25")

        # Assign the grade and save
        graded_statement = self.statement_repository.assign_grade(
            command.statement_id, command.grade, command.grader_id, command.comments
        )

        # Publish event
        event = StatementGradedEvent(
            aggregate_id=str(statement.id),
            data={
                "student_id": str(statement.student.id),
                "area_of_law": statement.area_of_law.name,
                "grade": command.grade,
                "grader_id": command.grader_id,
            },
        )
        self.event_bus.publish(event)

        return graded_statement


@dataclass
class CreateAreaCommand(Command):
    """Command to create an area of law"""

    name: str
    description: str = ""


class CreateAreaCommandHandler(CommandHandler[CreateAreaCommand]):
    """Handler for CreateAreaCommand"""

    def __init__(self, area_repository: AreaOfLawRepository):
        self.area_repository = area_repository

    async def handle(self, command: CreateAreaCommand) -> AreaOfLaw:
        """Handle the create area command"""
        # Check if an area with this name already exists
        existing = self.area_repository.model.objects.filter(name=command.name).first()
        if existing:
            raise ValueError(f"Area of law '{command.name}' already exists")

        return self.area_repository.create(
            name=command.name, description=command.description
        )


@dataclass
class ImportGradesCommand(Command):
    """Command to import grades from a file"""

    file_path: str
    imported_by_id: str


class ImportGradesCommandHandler(CommandHandler[ImportGradesCommand]):
    """Handler for ImportGradesCommand"""

    def __init__(
        self,
        grade_import_repository: GradeImportRepository,
        statement_repository: StatementRepository,
        event_bus: EventBus,
    ):
        self.grade_import_repository = grade_import_repository
        self.statement_repository = statement_repository
        self.event_bus = event_bus

    @transaction.atomic
    async def handle(self, command: ImportGradesCommand) -> Tuple[int, int, List[str]]:
        """Handle the import grades command"""
        success_count = 0
        error_count = 0
        errors = []

        # Implementation would depend on file format (CSV parsing, PDF extraction, etc.)
        # This is a simplified placeholder

        # Create import record
        self.grade_import_repository.create_import_record(
            imported_by_id=command.imported_by_id,
            file_name=command.file_path.split("/")[-1],
            success_count=success_count,
            error_count=error_count,
            errors="\n".join(errors),
        )

        return success_count, error_count, errors
