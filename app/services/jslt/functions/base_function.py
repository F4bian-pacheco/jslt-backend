"""Base class for JSLT functions."""
from abc import ABC, abstractmethod
from typing import Any


class BaseFunction(ABC):
    """Abstract base class for JSLT functions."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the function."""
        pass

    @abstractmethod
    def execute(self, *args: Any) -> Any:
        """
        Execute the function with the given arguments.

        Args:
            *args: Variable number of arguments for the function

        Returns:
            The result of executing the function

        Raises:
            ValueError: If the arguments are invalid
        """
        pass

    @property
    def description(self) -> str:
        """Return a description of what the function does."""
        return f"Function: {self.name}"
