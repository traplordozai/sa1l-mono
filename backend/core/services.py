from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class BaseService(Generic[T, ID], ABC):
    """
    Base service interface for domain services.

    This abstract class defines the contract for services that operate
    on domain entities and encapsulate business logic.
    """

    @abstractmethod
    def get_by_id(self, id: ID) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            id: The entity's ID

        Returns:
            The entity if found, otherwise None
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Retrieve all entities.

        Returns:
            List of all entities
        """
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.

        Args:
            data: The data for the new entity

        Returns:
            The newly created entity
        """
        pass

    @abstractmethod
    def update(self, id: ID, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing entity.

        Args:
            id: The entity's ID
            data: The updated data

        Returns:
            The updated entity, or None if not found
        """
        pass

    @abstractmethod
    def delete(self, id: ID) -> bool:
        """
        Delete an entity.

        Args:
            id: The entity's ID

        Returns:
            True if successful, False otherwise
        """
        pass


class DomainService(ABC):
    """
    Base class for domain-specific services that implement complex business logic.

    Domain services encapsulate business rules and operations that don't naturally
    belong to a single entity or value object.
    """

    pass
