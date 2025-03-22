from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from django.db.models import Model, Q, QuerySet

T = TypeVar("T", bound=Model)


class Specification(Generic[T], ABC):
    """
    Base Specification class for implementing the Specification Pattern.
    This pattern allows complex query criteria to be composed through multiple
    specification objects that can be combined using logical operators.
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the given entity satisfies this specification."""
        pass

    @abstractmethod
    def to_query(self) -> Q:
        """Convert this specification to a Django Q object for querying."""
        pass

    def __and__(self, other: "Specification[T]") -> "AndSpecification[T]":
        """Combine with another specification using AND."""
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "OrSpecification[T]":
        """Combine with another specification using OR."""
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        """Negate this specification."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Specification representing the logical AND of two specifications."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(
            candidate
        )

    def to_query(self) -> Q:
        return self.left.to_query() & self.right.to_query()


class OrSpecification(Specification[T]):
    """Specification representing the logical OR of two specifications."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(
            candidate
        )

    def to_query(self) -> Q:
        return self.left.to_query() | self.right.to_query()


class NotSpecification(Specification[T]):
    """Specification representing the logical NOT of a specification."""

    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)

    def to_query(self) -> Q:
        return ~self.spec.to_query()


class FieldEqualSpecification(Specification[T]):
    """Specification for field equality."""

    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, candidate: T) -> bool:
        return getattr(candidate, self.field) == self.value

    def to_query(self) -> Q:
        return Q(**{self.field: self.value})


class FieldInSpecification(Specification[T]):
    """Specification for field value in a collection."""

    def __init__(self, field: str, values: List[Any]):
        self.field = field
        self.values = values

    def is_satisfied_by(self, candidate: T) -> bool:
        return getattr(candidate, self.field) in self.values

    def to_query(self) -> Q:
        return Q(**{f"{self.field}__in": self.values})


class FieldContainsSpecification(Specification[T]):
    """Specification for text field containing a substring."""

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def is_satisfied_by(self, candidate: T) -> bool:
        field_value = str(getattr(candidate, self.field))
        return self.value.lower() in field_value.lower()

    def to_query(self) -> Q:
        return Q(**{f"{self.field}__icontains": self.value})


class PageSpec:
    """
    Specification for pagination.
    """

    def __init__(self, page: int = 1, size: int = 20):
        self.page = max(1, page)  # Page numbers start at 1
        self.size = max(1, min(100, size))  # Limit size between 1 and 100

    @property
    def offset(self) -> int:
        """Calculate the offset for this page"""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Get the limit (page size)"""
        return self.size
