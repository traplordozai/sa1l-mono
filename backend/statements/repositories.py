# backend/statements/repositories.py
from typing import Any, Dict, List, Optional

from django.db.models import Count, Q
from django.utils import timezone

from backend.core.repositories import BaseRepository

from .models import (AreaOfLaw, GradeImport, GradingRubric, RubricCriterion,
                     Statement)


class StatementRepository(BaseRepository):
    """
    Repository for Statement entity operations.
    """

    model = Statement

    def get_by_student(self, student_id: str) -> List[Statement]:
        """
        Get all statements for a specific student.

        Args:
            student_id: The ID of the student

        Returns:
            List of Statement objects
        """
        return self.model.objects.filter(student_id=student_id)

    def get_by_area_of_law(self, area_id: str) -> List[Statement]:
        """
        Get all statements for a specific area of law.

        Args:
            area_id: The ID of the area of law

        Returns:
            List of Statement objects
        """
        return self.model.objects.filter(area_of_law_id=area_id)

    def get_ungraded_statements(self) -> List[Statement]:
        """
        Get all ungraded statements.

        Returns:
            List of Statement objects
        """
        return self.model.objects.filter(grade__isnull=True)

    def get_graded_statements(self) -> List[Statement]:
        """
        Get all graded statements.

        Returns:
            List of Statement objects
        """
        return self.model.objects.filter(grade__isnull=False)

    def get_graded_by(self, grader_id: str) -> List[Statement]:
        """
        Get all statements graded by a specific user.

        Args:
            grader_id: The ID of the grader (User)

        Returns:
            List of Statement objects
        """
        return self.model.objects.filter(graded_by_id=grader_id)

    def search(self, query: str) -> List[Statement]:
        """
        Search statements by content or student name.

        Args:
            query: The search query

        Returns:
            List of matching Statement objects
        """
        return self.model.objects.filter(
            Q(content__icontains=query)
            | Q(student__first_name__icontains=query)
            | Q(student__last_name__icontains=query)
        )

    def assign_grade(self, statement_id: str, grade: int, grader_id: str) -> Statement:
        """
        Assign a grade to a statement.

        Args:
            statement_id: The ID of the statement
            grade: The grade value (0-25)
            grader_id: The ID of the grader (User)

        Returns:
            Updated Statement object
        """
        statement = self.get_by_id(statement_id)
        statement.grade = grade
        statement.graded_by_id = grader_id
        statement.graded_at = timezone.now()
        statement.save()
        return statement


class AreaOfLawRepository(BaseRepository):
    """
    Repository for AreaOfLaw entity operations.
    """

    model = AreaOfLaw

    def get_with_statement_count(self) -> List[Dict[str, Any]]:
        """
        Get all areas of law with the count of associated statements.

        Returns:
            List of dicts with area info and statement count
        """
        areas = self.model.objects.annotate(statement_count=Count("statements"))
        return [
            {
                "id": area.id,
                "name": area.name,
                "description": area.description,
                "statement_count": area.statement_count,
            }
            for area in areas
        ]


class GradingRubricRepository(BaseRepository):
    """
    Repository for GradingRubric entity operations.
    """

    model = GradingRubric

    def get_active_for_area(self, area_id: str) -> Optional[GradingRubric]:
        """
        Get the active rubric for a specific area of law.

        Args:
            area_id: The ID of the area of law

        Returns:
            Active GradingRubric or None
        """
        return self.model.objects.filter(area_of_law_id=area_id, is_active=True).first()

    def get_with_criteria(self, rubric_id: str) -> Optional[GradingRubric]:
        """
        Get a rubric with all its criteria preloaded.

        Args:
            rubric_id: The ID of the rubric

        Returns:
            GradingRubric with prefetched criteria or None
        """
        return (
            self.model.objects.prefetch_related("criteria").filter(id=rubric_id).first()
        )


class GradeImportRepository(BaseRepository):
    """
    Repository for GradeImport entity operations.
    """

    model = GradeImport

    def create_import_record(
        self,
        imported_by_id: str,
        file_name: str,
        success_count: int = 0,
        error_count: int = 0,
        errors: str = "",
    ) -> GradeImport:
        """
        Create a new grade import record.

        Args:
            imported_by_id: User ID who performed the import
            file_name: Name of the imported file
            success_count: Number of successfully imported grades
            error_count: Number of import errors
            errors: Error details as text

        Returns:
            Created GradeImport object
        """
        return self.model.objects.create(
            imported_by_id=imported_by_id,
            file_name=file_name,
            success_count=success_count,
            error_count=error_count,
            errors=errors,
        )
