from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)


class BaseRepository(Generic[T]):
    """
    Base repository class implementing the repository pattern.

    This abstract class provides a standard interface for data access operations
    and helps decouple the domain logic from the data access layer.
    """
    model_class: Type[T]

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def get_queryset(self) -> QuerySet[T]:
        """
        Get the base queryset for this repository.

        Returns:
            QuerySet for the model
        """
        return self.model_class.objects.all()

    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            id: The primary key value

        Returns:
            The entity if found, otherwise None
        """
        try:
            return self.get_queryset().get(pk=id)
        except self.model_class.DoesNotExist:
            return None

    def get_all(self) -> List[T]:
        """
        Retrieve all entities.

        Returns:
            List of all entities
        """
        return list(self.get_queryset())

    def find(self, **kwargs) -> List[T]:
        """
        Find entities matching the given criteria.

        Args:
            **kwargs: Field lookups to filter by

        Returns:
            List of matching entities
        """
        return list(self.get_queryset().filter(**kwargs))

    def find_one(self, **kwargs) -> Optional[T]:
        """
        Find a single entity matching the given criteria.

        Args:
            **kwargs: Field lookups to filter by

        Returns:
            The first matching entity, or None if not found
        """
        try:
            return self.get_queryset().filter(**kwargs).first()
        except self.model_class.DoesNotExist:
            return None

    def create(self, **kwargs) -> T:
        """
        Create a new entity with the given attributes.

        Args:
            **kwargs: Attributes for the new entity

        Returns:
            The newly created entity
        """
        return self.model_class.objects.create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        """
        Update an entity with the given attributes.

        Args:
            instance: The entity to update
            **kwargs: Attributes to update

        Returns:
            The updated entity
        """
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        """
        Delete an entity.

        Args:
            instance: The entity to delete
        """
        instance.delete()


class BaseActiveRepository(BaseRepository[T]):
    """
    Repository for models that inherit from BaseActiveModel.
    Automatically filters to only show active records.
    """

    def get_queryset(self) -> QuerySet[T]:
        """
        Get the base queryset, filtering for active records only.

        Returns:
            QuerySet of active records
        """
        return self.model_class.objects.filter(is_active=True)

    def get_all_including_inactive(self) -> List[T]:
        """
        Get all records including inactive ones.

        Returns:
            List of all records
        """
        return list(self.model_class.objects.all())

    def soft_delete(self, instance: T) -> T:
        """
        Soft delete an entity by marking it as inactive.

        Args:
            instance: The entity to soft delete

        Returns:
            The updated entity
        """
        instance.deactivate()
        return instance