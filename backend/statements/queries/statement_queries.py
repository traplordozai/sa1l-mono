from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.db.models import Avg, Count
from statements.models import AreaOfLaw, GradingRubric, Statement
from statements.repositories import (AreaOfLawRepository,
                                     GradingRubricRepository,
                                     StatementRepository)

from backend.core.cqrs import Query, QueryHandler


@dataclass
class GetStudentStatementsQuery(Query):
    """Query to get all statements for a student"""

    student_id: str


class GetStudentStatementsQueryHandler(
    QueryHandler[GetStudentStatementsQuery, List[Statement]]
):
    """Handler for GetStudentStatementsQuery"""

    def __init__(self, statement_repository: StatementRepository):
        self.statement_repository = statement_repository

    async def handle(self, query: GetStudentStatementsQuery) -> List[Statement]:
        """Handle the get student statements query"""
        return self.statement_repository.get_by_student(query.student_id)


@dataclass
class GetUngradedStatementsQuery(Query):
    """Query to get all ungraded statements"""

    pass


class GetUngradedStatementsQueryHandler(
    QueryHandler[GetUngradedStatementsQuery, List[Statement]]
):
    """Handler for GetUngradedStatementsQuery"""

    def __init__(self, statement_repository: StatementRepository):
        self.statement_repository = statement_repository

    async def handle(self, query: GetUngradedStatementsQuery) -> List[Statement]:
        """Handle the get ungraded statements query"""
        return self.statement_repository.get_ungraded_statements()


@dataclass
class GetGradingStatisticsQuery(Query):
    """Query to get grading statistics"""

    pass


class GetGradingStatisticsQueryHandler(
    QueryHandler[GetGradingStatisticsQuery, Dict[str, Any]]
):
    """Handler for GetGradingStatisticsQuery"""

    def __init__(self, statement_repository: StatementRepository):
        self.statement_repository = statement_repository

    async def handle(self, query: GetGradingStatisticsQuery) -> Dict[str, Any]:
        """Handle the get grading statistics query"""
        ungraded_count = self.statement_repository.model.objects.filter(
            grade__isnull=True
        ).count()
        graded_count = self.statement_repository.model.objects.filter(
            grade__isnull=False
        ).count()
        total_count = ungraded_count + graded_count

        # Get average grade by area of law
        area_stats = []
        for area in (
            self.statement_repository.model.objects.values("area_of_law__name")
            .annotate(avg_grade=Avg("grade"), count=Count("id"))
            .filter(grade__isnull=False)
        ):
            area_stats.append(
                {
                    "area": area["area_of_law__name"],
                    "average_grade": (
                        round(area["avg_grade"], 2) if area["avg_grade"] else None
                    ),
                    "count": area["count"],
                }
            )

        return {
            "total_statements": total_count,
            "graded_statements": graded_count,
            "ungraded_statements": ungraded_count,
            "completion_percentage": (
                round((graded_count / total_count) * 100, 1) if total_count > 0 else 0
            ),
            "area_statistics": area_stats,
        }


@dataclass
class GetRubricForStatementQuery(Query):
    """Query to get the rubric for a statement"""

    statement_id: str


class GetRubricForStatementQueryHandler(
    QueryHandler[GetRubricForStatementQuery, Optional[GradingRubric]]
):
    """Handler for GetRubricForStatementQuery"""

    def __init__(
        self,
        statement_repository: StatementRepository,
        rubric_repository: GradingRubricRepository,
    ):
        self.statement_repository = statement_repository
        self.rubric_repository = rubric_repository

    async def handle(
        self, query: GetRubricForStatementQuery
    ) -> Optional[GradingRubric]:
        """Handle the get rubric for statement query"""
        statement = self.statement_repository.get_by_id(query.statement_id)
        if not statement:
            raise ValueError(f"Statement with ID {query.statement_id} not found")

        return self.rubric_repository.get_active_for_area(statement.area_of_law_id)


@dataclass
class GetAllAreasQuery(Query):
    """Query to get all areas of law"""

    pass


class GetAllAreasQueryHandler(QueryHandler[GetAllAreasQuery, List[AreaOfLaw]]):
    """Handler for GetAllAreasQuery"""

    def __init__(self, area_repository: AreaOfLawRepository):
        self.area_repository = area_repository

    async def handle(self, query: GetAllAreasQuery) -> List[AreaOfLaw]:
        """Handle the get all areas query"""
        return self.area_repository.get_all()


@dataclass
class GetAreasWithStatementCountQuery(Query):
    """Query to get areas with statement counts"""

    pass


class GetAreasWithStatementCountQueryHandler(
    QueryHandler[GetAreasWithStatementCountQuery, List[Dict[str, Any]]]
):
    """Handler for GetAreasWithStatementCountQuery"""

    def __init__(self, area_repository: AreaOfLawRepository):
        self.area_repository = area_repository

    async def handle(
        self, query: GetAreasWithStatementCountQuery
    ) -> List[Dict[str, Any]]:
        """Handle the get areas with statement count query"""
        return self.area_repository.get_with_statement_count()
