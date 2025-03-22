# backend/students/event_handlers.py
import logging

from core.events import (StatementGradedEvent, StudentCreatedEvent,
                         StudentMatchedEvent, StudentUpdatedEvent)
from core.handlers import EventHandler

logger = logging.getLogger(__name__)


class StudentEventHandler(EventHandler):
    """
    Handles student-related domain events
    """

    def handle_StudentCreatedEvent(self, event: StudentCreatedEvent) -> None:
        """
        Handle student creation event
        """
        logger.info(f"New student created: {event.aggregate_id}")
        # Additional logic such as sending welcome email, updating statistics, etc.

    def handle_StudentUpdatedEvent(self, event: StudentUpdatedEvent) -> None:
        """
        Handle student update event
        """
        logger.info(f"Student updated: {event.aggregate_id}")
        # Handle profile updates, check completion, etc.

    def handle_StudentMatchedEvent(self, event: StudentMatchedEvent) -> None:
        """
        Handle student matching event
        """
        logger.info(f"Student matched: {event.aggregate_id}")
        # Send notification, update student status

        # Extract match details from event data
        match_data = event.data.get("match", {})
        organization_id = match_data.get("organization_id")

        if organization_id:
            # Update student's match status
            from students.models import Student

            try:
                student = Student.objects.get(id=event.aggregate_id)
                student.is_matched = True
                student.save(update_fields=["is_matched"])
            except Student.DoesNotExist:
                logger.error(f"Student not found: {event.aggregate_id}")

    def handle_StatementGradedEvent(self, event: StatementGradedEvent) -> None:
        """
        Handle statement grading event
        """
        logger.info(f"Statement graded for student: {event.data.get('student_id')}")
        # Update student's statement status, recalculate metrics
