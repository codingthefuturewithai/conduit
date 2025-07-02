from abc import ABC, abstractmethod
from typing import Any, Dict


class Platform(ABC):
    """Base class for all platform implementations."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the platform."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the platform."""
        pass


class IssueManager(ABC):
    """Base class for issue management."""

    @abstractmethod
    def get(self, key: str) -> Dict[str, Any]:
        """Get issue by key."""
        pass

    @abstractmethod
    def search(self, query: str) -> list[Dict[str, Any]]:
        """Search for issues."""
        pass

    @abstractmethod
    def create(self, **kwargs) -> Dict[str, Any]:
        """Create a new issue."""
        pass

    @abstractmethod
    def update(self, key: str, **kwargs) -> None:
        """Update an existing issue."""
        pass
