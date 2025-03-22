from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Count, Prefetch, Q

from backend.core.repositories import BaseActiveRepository, BaseRepository
from backend.core.specifications import PageSpec, Specification

from .models import (AreaOfLaw, SelfProposedExternship, Statement, Student,
                     StudentAreaRanking, StudentGrade)
from .specifications import StudentSearchSpecification


class StudentRepository(BaseActiveRepository[Student]):
    """Repository for Student entities."""

    model_class = Student

    def get_by_student_id(self, student_id: str) -> Optional[Student]:
        """Get a student by their student ID."""
        return self.find_one(student_id=student_id)

    def search_students(self, query: str) -> List[Student]:
        """
        Search for students based on a query string.
        Searches across multiple fields.
        """
        spec = StudentSearchSpecification(query)
        return self.find_with_specification(spec)

    def search_students_paginated(
        self, query: str, page: int = 1, size: int = 20
    ) -> Tuple[List[Student], Dict[str, Any]]:
        """
        Search for students with pagination.

        Args:
            query: Search query
            page: Page number
            size: Page size

        Returns:
            Tuple of (list of students, pagination metadata)
        """
        spec = StudentSearchSpecification(query)
        page_spec = PageSpec(page, size)
        return self.find_paginated_with_specification(spec, page_spec)

    def get_by_program(self, program: str) -> List[Student]:
        """Get all students in a specific program."""
        return self.find(program=program)

    def get_matched_students(self) -> List[Student]:
        """Get all students who have been matched."""
        return self.find(is_matched=True)

    def get_unmatched_students(self) -> List[Student]:
        """Get all students who haven't been matched yet."""
        return self.find(is_matched=False)

    def save(self, student: Student) -> Student:
        """
        Save a student instance after validating.

        Args:
            student: Student instance to save

        Returns:
            Saved student instance
        """
        student.validate_and_raise()
        student.save()
        return student


class StudentGradeRepository(BaseRepository[StudentGrade]):
    """Repository for StudentGrade entities."""

    def __init__(self):
        super().__init__(StudentGrade)

    def get_by_student(self, student):
        """Get grades for a specific student."""
        return self.find_one(student=student)

    def get_by_student_id(self, student_id):
        """Get grades by student ID."""
        return self.get_queryset().filter(student__student_id=student_id).first()


class StatementRepository(BaseRepository[Statement]):
    """Repository for Statement entities."""

    def __init__(self):
        super().__init__(Statement)

    def get_by_student(self, student):
        """Get statements for a specific student."""
        return self.find(student=student)

    def get_by_area(self, area):
        """Get statements for a specific area of law."""
        return self.find(area_of_law=area)

    def get_graded_statements(self):
        """Get statements that have been graded."""
        return self.get_queryset().filter(statement_grade__isnull=False)

    def get_ungraded_statements(self):
        """Get statements that have not been graded."""
        return self.get_queryset().filter(statement_grade__isnull=True)


class AreaOfLawRepository(BaseRepository[AreaOfLaw]):
    """Repository for AreaOfLaw entities."""

    def __init__(self):
        super().__init__(AreaOfLaw)

    def get_by_name(self, name):
        """Get an area of law by name."""
        return self.find_one(name=name)

    def get_popular_areas(self, limit=5):
        """Get the most popular areas based on student rankings."""
        return (
            self.get_queryset()
            .annotate(num_students=Count("studentarearanking"))
            .order_by("-num_students")[:limit]
        )


class StudentAreaRankingRepository(BaseRepository[StudentAreaRanking]):
    """Repository for StudentAreaRanking entities."""

    def __init__(self):
        super().__init__(StudentAreaRanking)

    def get_by_student(self, student):
        """Get area rankings for a specific student."""
        return self.find(student=student)

    def get_by_area(self, area):
        """Get student rankings for a specific area."""
        return self.find(area=area)

    def get_top_ranked_areas_for_student(self, student, limit=3):
        """Get a student's top ranked areas."""
        return self.get_queryset().filter(student=student).order_by("rank")[:limit]


class SelfProposedExternshipRepository(BaseRepository[SelfProposedExternship]):
    """Repository for SelfProposedExternship entities."""

    def __init__(self):
        super().__init__(SelfProposedExternship)

    def get_by_student(self, student):
        """Get self-proposed externship for a specific student."""
        return self.find_one(student=student)
