from django.db.models import Q

from backend.core.specifications import (FieldContainsSpecification,
                                         FieldEqualSpecification,
                                         Specification)

from .models import Student


class StudentActiveSpecification(Specification[Student]):
    """Specification for active students."""

    def is_satisfied_by(self, candidate: Student) -> bool:
        return candidate.is_active

    def to_query(self) -> Q:
        return Q(is_active=True)


class StudentMatchedSpecification(Specification[Student]):
    """Specification for matched students."""

    def __init__(self, is_matched: bool = True):
        self.is_matched = is_matched

    def is_satisfied_by(self, candidate: Student) -> bool:
        return candidate.is_matched == self.is_matched

    def to_query(self) -> Q:
        return Q(is_matched=self.is_matched)


class StudentProgramSpecification(FieldEqualSpecification[Student]):
    """Specification for students in a specific program."""

    def __init__(self, program: str):
        super().__init__("program", program)


class StudentNameSpecification(Specification[Student]):
    """Specification for students with matching name."""

    def __init__(self, name: str):
        self.name = name.lower()

    def is_satisfied_by(self, candidate: Student) -> bool:
        return (
            self.name in candidate.first_name.lower()
            or self.name in candidate.last_name.lower()
        )

    def to_query(self) -> Q:
        return Q(first_name__icontains=self.name) | Q(last_name__icontains=self.name)


class StudentSearchSpecification(Specification[Student]):
    """
    Comprehensive search specification for students.
    Searches across multiple fields.
    """

    def __init__(self, search_term: str):
        self.search_term = search_term.lower()

    def is_satisfied_by(self, candidate: Student) -> bool:
        # Check various fields for the search term
        if self.search_term in candidate.student_id.lower():
            return True
        if self.search_term in candidate.first_name.lower():
            return True
        if self.search_term in candidate.last_name.lower():
            return True
        if self.search_term in candidate.email.lower():
            return True
        if (
            hasattr(candidate, "program")
            and self.search_term in candidate.program.lower()
        ):
            return True
        return False

    def to_query(self) -> Q:
        return (
            Q(student_id__icontains=self.search_term)
            | Q(first_name__icontains=self.search_term)
            | Q(last_name__icontains=self.search_term)
            | Q(email__icontains=self.search_term)
            | Q(program__icontains=self.search_term)
        )
