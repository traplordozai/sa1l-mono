# backend/core/handlers.py
import inspect
import logging
from typing import Any, Callable, Dict, List, Set, Type

from .events import DomainEvent

logger = logging.getLogger(__name__)


class EventHandler:
    """
    Base class for all event handlers
    """

    def __init__(self):
        self.event_types = self._discover_handled_events()

    def _discover_handled_events(self) -> Set[Type[DomainEvent]]:
        """
        Automatically discover event types this handler can process
        based on method names starting with 'handle_'
        """
        handled_events = set()

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('handle_'):
                # Extract event class name from method name (handle_EventName)
                event_name = name[7:]  # Remove 'handle_' prefix
                # Find the event class from the events module
                for event_cls in DomainEvent.__subclasses__():
                    if event_cls.__name__ == event_name:
                        handled_events.add(event_cls)
                        break

        return handled_events

    def can_handle(self, event: DomainEvent) -> bool:
        """
        Check if this handler can process the given event
        """
        return type(event) in self.event_types

    def handle(self, event: DomainEvent) -> None:
        """
        Process the event by dispatching to the appropriate handler method
        """
        method_name = f"handle_{event.__class__.__name__}"
        handler_method = getattr(self, method_name, None)

        if handler_method and callable(handler_method):
            try:
                handler_method(event)
            except Exception as e:
                logger.exception(f"Error handling event {event.event_type}: {str(e)}")
                raise
        else:
            logger.warning(f"No handler method found for event {event.event_type}")


class EventBus:
    """
    Central event dispatcher that routes events to registered handlers
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.handlers = []
        return cls._instance

    def register_handler(self, handler: EventHandler) -> None:
        """
        Register an event handler
        """
        if handler not in self.handlers:
            self.handlers.append(handler)
            logger.info(f"Registered event handler: {handler.__class__.__name__}")

    def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all registered handlers
        """
        logger.debug(f"Publishing event: {event.event_type}")

        handled = False
        for handler in self.handlers:
            if handler.can_handle(event):
                handler.handle(event)
                handled = True

        if not handled:
            logger.warning(f"No handlers found for event: {event.event_type}")