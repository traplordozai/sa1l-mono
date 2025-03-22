# backend/matching/event_handlers.py
import logging

from core.events import (MatchApprovedEvent, MatchCreatedEvent,
                         MatchRejectedEvent, StudentMatchedEvent)
from core.handlers import EventHandler

logger = logging.getLogger(__name__)


class MatchingEventHandler(EventHandler):
    """
    Handles matching-related domain events
    """

    def handle_MatchCreatedEvent(self, event: MatchCreatedEvent) -> None:
        """
        Handle match creation event
        """
        logger.info(f"New match created: {event.aggregate_id}")
        # Update statistics, send notifications

    def handle_MatchApprovedEvent(self, event: MatchApprovedEvent) -> None:
        """
        Handle match approval event
        """
        logger.info(f"Match approved: {event.aggregate_id}")

        # Extract match details from event data
        match_data = event.data
        student_id = match_data.get("student_id")
        organization_id = match_data.get("organization_id")

        if student_id and organization_id:
            # Update organization's filled positions
            from organizations.models import Organization

            try:
                organization = Organization.objects.get(id=organization_id)
                organization.filled_positions += 1
                organization.save(update_fields=["filled_positions"])
            except Organization.DoesNotExist:
                logger.error(f"Organization not found: {organization_id}")

    def handle_MatchRejectedEvent(self, event: MatchRejectedEvent) -> None:
        """
        Handle match rejection event
        """
        logger.info(f"Match rejected: {event.aggregate_id}")
        # Reset student status, notify admin

    def handle_StudentMatchedEvent(self, event: StudentMatchedEvent) -> None:
        """
        Handle student matched event from student domain
        """
        logger.info(f"Student matched event received: {event.aggregate_id}")
        # Sync matching domain with student domain events
