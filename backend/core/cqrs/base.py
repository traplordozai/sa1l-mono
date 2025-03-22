from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class Command(ABC):
    """Base class for all commands"""

    pass


class CommandHandler(Generic[T], ABC):
    """Base class for all command handlers"""

    @abstractmethod
    async def handle(self, command: T) -> Any:
        """Handle the given command"""
        pass


class Query(ABC):
    """Base class for all queries"""

    pass


class QueryHandler(Generic[T, R], ABC):
    """Base class for all query handlers"""

    @abstractmethod
    async def handle(self, query: T) -> R:
        """Handle the given query"""
        pass
