from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from students.models import Student
from students.repositories import (SelfProposedExternshipRepository,
                                   StatementRepository,
                                   StudentAreaRankingRepository,
                                   StudentGradeRepository, StudentRepository)

from backend.core.cqrs import Query, QueryHandler


@dataclass
class GetStudentByIdQuery(Query):
    """Query to get a student by ID"""

    id: str


class GetStudentByIdQueryHandler(QueryHandler[GetStudentByIdQuery, Optional[Student]]):
    """Handler for GetStudentByIdQuery"""

    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def handle(self, query: GetStudentByIdQuery) -> Optional[Student]:
        """Handle the get student by ID query"""
        return self.student_repository.get_by_id(query.id)


@dataclass
class GetAllStudentsQuery(Query):
    """Query to get all students"""

    pass


class GetAllStudentsQueryHandler(QueryHandler[GetAllStudentsQuery, List[Student]]):
    """Handler for GetAllStudentsQuery"""

    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def handle(self, query: GetAllStudentsQuery) -> List[Student]:
        """Handle the get all students query"""
        return self.student_repository.get_all()


@dataclass
class GetStudentProfileQuery(Query):
    """Query to get a complete student profile"""

    student_id: str


class GetStudentProfileQueryHandler(
    QueryHandler[GetStudentProfileQuery, Dict[str, Any]]
):
    """Handler for GetStudentProfileQuery"""

    def __init__(
        self,
        student_repository: StudentRepository,
        grade_repository: StudentGradeRepository,
        statement_repository: StatementRepository,
        ranking_repository: StudentAreaRankingRepository,
        externship_repository: SelfProposedExternshipRepository,
    ):
        self.student_repository = student_repository
        self.grade_repository = grade_repository
        self.statement_repository = statement_repository
        self.ranking_repository = ranking_repository
        self.externship_repository = externship_repository

    async def handle(self, query: GetStudentProfileQuery) -> Dict[str, Any]:
        """Handle the get student profile query"""
        student = self.student_repository.get_by_id(query.student_id)
        if not student:
            return {}

        grades = self.grade_repository.get_by_student(student)
        statements = self.statement_repository.get_by_student(student)
        area_rankings = self.ranking_repository.get_by_student(student)
        self_proposed = self.externship_repository.get_by_student(student)

        return {
            "student": student,
            "grades": grades,
            "statements": statements,
            "area_rankings": area_rankings,
            "self_proposed_externship": self_proposed,
        }


@dataclass
class SearchStudentsQuery(Query):
    """Query to search for students"""

    query: str
    filters: Dict[str, Any] = None


class SearchStudentsQueryHandler(QueryHandler[SearchStudentsQuery, List[Student]]):
    """Handler for SearchStudentsQuery"""

    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def handle(self, query: SearchStudentsQuery) -> List[Student]:
        """Handle the search students query"""
        students = self.student_repository.search_students(query.query)

        # Apply additional filters if provided
        if query.filters:
            if "program" in query.filters and query.filters["program"]:
                students = [
                    s for s in students if s.program == query.filters["program"]
                ]

            if "is_matched" in query.filters:
                students = [
                    s for s in students if s.is_matched == query.filters["is_matched"]
                ]

            if "is_active" in query.filters:
                students = [
                    s for s in students if s.is_active == query.filters["is_active"]
                ]

        return students
