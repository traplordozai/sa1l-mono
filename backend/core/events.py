# backend/core/events.py
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Type


class DomainEvent:
    """
    Base class for all domain events
    """

    def __init__(
        self,
        aggregate_id: str,
        data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
    ):
        self.id = str(uuid.uuid4())
        self.aggregate_id = aggregate_id
        self.data = data or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.event_type = self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation
        """
        return {
            "id": self.id,
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """
        Create event instance from dictionary
        """
        event = cls(
            aggregate_id=data["aggregate_id"],
            data=data["data"],
            metadata=data["metadata"],
        )
        event.id = data["id"]
        event.timestamp = data["timestamp"]
        return event


# Student domain events
class StudentCreatedEvent(DomainEvent):
    """Event fired when a new student is created"""

    pass


class StudentUpdatedEvent(DomainEvent):
    """Event fired when a student profile is updated"""

    pass


class StudentMatchedEvent(DomainEvent):
    """Event fired when a student is matched with an organization"""

    pass


# Organization domain events
class OrganizationCreatedEvent(DomainEvent):
    """Event fired when a new organization is created"""

    pass


class OrganizationUpdatedEvent(DomainEvent):
    """Event fired when an organization profile is updated"""

    pass


# Statement domain events
class StatementSubmittedEvent(DomainEvent):
    """Event fired when a student submits a statement"""

    pass


class StatementGradedEvent(DomainEvent):
    """Event fired when a statement is graded"""

    pass


# Match domain events
class MatchCreatedEvent(DomainEvent):
    """Event fired when a match is created"""

    pass


class MatchApprovedEvent(DomainEvent):
    """Event fired when a match is approved"""

    pass


class MatchRejectedEvent(DomainEvent):
    """Event fired when a match is rejected"""

    pass


# Import domain events
class ImportCompletedEvent(DomainEvent):
    """Event fired when an import is completed"""

    pass
