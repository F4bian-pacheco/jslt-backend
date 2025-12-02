"""Built-in JSLT functions."""
from typing import Any, Union
from .base_function import BaseFunction


class SizeFunction(BaseFunction):
    """Get size of array, object, or string."""

    @property
    def name(self) -> str:
        return "size"

    def execute(self, value: Any) -> int:
        """Get size of array, object, or string."""
        if isinstance(value, (list, dict, str)):
            return len(value)
        return 0

    @property
    def description(self) -> str:
        return "Returns the size of an array, object, or string"


class StringFunction(BaseFunction):
    """Convert value to string."""

    @property
    def name(self) -> str:
        return "string"

    def execute(self, value: Any) -> str:
        """Convert value to string."""
        if value is None:
            return ""
        return str(value)

    @property
    def description(self) -> str:
        return "Converts a value to a string"


class NumberFunction(BaseFunction):
    """Convert value to number."""

    @property
    def name(self) -> str:
        return "number"

    def execute(self, value: Any) -> Union[int, float]:
        """Convert value to number."""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return int(value) if value.isdigit() else float(value)
            except ValueError:
                return 0
        return 0

    @property
    def description(self) -> str:
        return "Converts a value to a number"


class BooleanFunction(BaseFunction):
    """Convert value to boolean."""

    @property
    def name(self) -> str:
        return "boolean"

    def execute(self, value: Any) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        if isinstance(value, (int, float)):
            return value != 0
        return bool(value)

    @property
    def description(self) -> str:
        return "Converts a value to a boolean"


class RoundFunction(BaseFunction):
    """Round number to nearest integer."""

    @property
    def name(self) -> str:
        return "round"

    def execute(self, value: Union[int, float]) -> int:
        """Round number to nearest integer."""
        return round(float(value))

    @property
    def description(self) -> str:
        return "Rounds a number to the nearest integer"


# Registry of all built-in functions
BUILTIN_FUNCTIONS = [
    SizeFunction(),
    StringFunction(),
    NumberFunction(),
    BooleanFunction(),
    RoundFunction(),
]
