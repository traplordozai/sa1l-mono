# backend/statements/services.py
import logging
from typing import Any, Dict, List, Optional, Tuple

from core.handlers import EventBus
from django.contrib.auth import get_user_model
from django.db import transaction

from backend.core.cqrs import CommandDispatcher, QueryDispatcher
from backend.core.services import BaseService
from backend.students.repositories import StudentRepository

from .commands.statement_commands import (CreateAreaCommand,
                                          CreateStatementCommand,
                                          DeleteStatementCommand,
                                          GradeStatementCommand,
                                          ImportGradesCommand,
                                          UpdateStatementCommand)
from .models import AreaOfLaw, GradeImport, GradingRubric, Statement
from .queries.statement_queries import (GetAllAreasQuery,
                                        GetAreasWithStatementCountQuery,
                                        GetGradingStatisticsQuery,
                                        GetRubricForStatementQuery,
                                        GetStudentStatementsQuery,
                                        GetUngradedStatementsQuery)
from .repositories import (AreaOfLawRepository, GradeImportRepository,
                           GradingRubricRepository, StatementRepository)

User = get_user_model()
logger = logging.getLogger(__name__)


class StatementService(BaseService):
    """
    Service for statement-related business logic.
    """

    def __init__(self):
        # Repositories
        self.statement_repository = StatementRepository()
        self.student_repository = StudentRepository()
        self.area_repository = AreaOfLawRepository()
        self.rubric_repository = GradingRubricRepository()
        self.grade_import_repository = GradeImportRepository()
        self.event_bus = EventBus()

        # Command dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.command_dispatcher.register(
            CreateStatementCommand,
            CreateStatementCommandHandler(
                self.statement_repository,
                self.student_repository,
                self.area_repository,
                self.event_bus,
            ),
        )
        self.command_dispatcher.register(
            UpdateStatementCommand,
            UpdateStatementCommandHandler(self.statement_repository),
        )
        self.command_dispatcher.register(
            DeleteStatementCommand,
            DeleteStatementCommandHandler(self.statement_repository),
        )
        self.command_dispatcher.register(
            GradeStatementCommand,
            GradeStatementCommandHandler(self.statement_repository, self.event_bus),
        )
        self.command_dispatcher.register(
            CreateAreaCommand, CreateAreaCommandHandler(self.area_repository)
        )
        self.command_dispatcher.register(
            ImportGradesCommand,
            ImportGradesCommandHandler(
                self.grade_import_repository, self.statement_repository, self.event_bus
            ),
        )

        # Query dispatcher
        self.query_dispatcher = QueryDispatcher()
        self.query_dispatcher.register(
            GetStudentStatementsQuery,
            GetStudentStatementsQueryHandler(self.statement_repository),
        )
        self.query_dispatcher.register(
            GetUngradedStatementsQuery,
            GetUngradedStatementsQueryHandler(self.statement_repository),
        )
        self.query_dispatcher.register(
            GetGradingStatisticsQuery,
            GetGradingStatisticsQueryHandler(self.statement_repository),
        )
        self.query_dispatcher.register(
            GetRubricForStatementQuery,
            GetRubricForStatementQueryHandler(
                self.statement_repository, self.rubric_repository
            ),
        )
        self.query_dispatcher.register(
            GetAllAreasQuery, GetAllAreasQueryHandler(self.area_repository)
        )
        self.query_dispatcher.register(
            GetAreasWithStatementCountQuery,
            GetAreasWithStatementCountQueryHandler(self.area_repository),
        )

    async def get_student_statements(self, student_id: str) -> List[Statement]:
        """Get all statements for a student."""
        query = GetStudentStatementsQuery(student_id=student_id)
        return await self.query_dispatcher.dispatch(query)

    async def create_statement(
        self, student_id: str, area_id: str, content: str
    ) -> Statement:
        """Create a new statement for a student."""
        command = CreateStatementCommand(
            student_id=student_id, area_id=area_id, content=content
        )
        return await self.command_dispatcher.dispatch(command)

    async def update_statement(self, statement_id: str, content: str) -> Statement:
        """Update an existing statement."""
        command = UpdateStatementCommand(statement_id=statement_id, content=content)
        return await self.command_dispatcher.dispatch(command)

    async def delete_statement(self, statement_id: str) -> None:
        """Delete a statement."""
        command = DeleteStatementCommand(statement_id=statement_id)
        return await self.command_dispatcher.dispatch(command)

    async def get_ungraded_statements(self) -> List[Statement]:
        """Get all statements that need grading."""
        query = GetUngradedStatementsQuery()
        return await self.query_dispatcher.dispatch(query)

    async def get_grading_statistics(self) -> Dict[str, Any]:
        """Get statistics about grading progress."""
        query = GetGradingStatisticsQuery()
        return await self.query_dispatcher.dispatch(query)

    async def grade_statement(
        self, statement_id: str, grade: int, grader_id: str, comments: str = ""
    ) -> Statement:
        """Grade a student's statement."""
        command = GradeStatementCommand(
            statement_id=statement_id,
            grade=grade,
            grader_id=grader_id,
            comments=comments,
        )
        return await self.command_dispatcher.dispatch(command)

    async def import_grades_from_file(
        self, file_path: str, imported_by_id: str
    ) -> Tuple[int, int, List[str]]:
        """Import grades from a file."""
        command = ImportGradesCommand(
            file_path=file_path, imported_by_id=imported_by_id
        )
        return await self.command_dispatcher.dispatch(command)

    async def get_rubric_for_statement(
        self, statement_id: str
    ) -> Optional[GradingRubric]:
        """Get the active grading rubric for a statement's area of law."""
        query = GetRubricForStatementQuery(statement_id=statement_id)
        return await self.query_dispatcher.dispatch(query)

    async def get_all_areas(self) -> List[AreaOfLaw]:
        """Get all areas of law."""
        query = GetAllAreasQuery()
        return await self.query_dispatcher.dispatch(query)

    async def get_areas_with_statement_count(self) -> List[Dict[str, Any]]:
        """Get all areas of law with statement counts."""
        query = GetAreasWithStatementCountQuery()
        return await self.query_dispatcher.dispatch(query)

    async def create_area(self, name: str, description: str = "") -> AreaOfLaw:
        """Create a new area of law."""
        command = CreateAreaCommand(name=name, description=description)
        return await self.command_dispatcher.dispatch(command)
