from typing import Any, Dict, Type

from .base import Command, CommandHandler, Query, QueryHandler


class CommandDispatcher:
    """Dispatches commands to their appropriate handlers"""

    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}

    def register(self, command_type: Type[Command], handler: CommandHandler) -> None:
        """Register a handler for a command type"""
        self._handlers[command_type] = handler

    async def dispatch(self, command: Command) -> Any:
        """Dispatch a command to its registered handler"""
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(
                f"No handler registered for command {type(command).__name__}"
            )
        return await handler.handle(command)


class QueryDispatcher:
    """Dispatches queries to their appropriate handlers"""

    def __init__(self):
        self._handlers: Dict[Type[Query], QueryHandler] = {}

    def register(self, query_type: Type[Query], handler: QueryHandler) -> None:
        """Register a handler for a query type"""
        self._handlers[query_type] = handler

    async def dispatch(self, query: Query) -> Any:
        """Dispatch a query to its registered handler"""
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query {type(query).__name__}")
        return await handler.handle(query)
