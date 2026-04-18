"""Built-in JSLT functions."""
import math
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


class LowercaseFunction(BaseFunction):
    """Convert text to lowercase."""

    @property
    def name(self) -> str:
        return "lowercase"

    def execute(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).lower()

    @property
    def description(self) -> str:
        return "Converts a value to lowercase text"


class UppercaseFunction(BaseFunction):
    """Convert text to uppercase."""

    @property
    def name(self) -> str:
        return "uppercase"

    def execute(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).upper()

    @property
    def description(self) -> str:
        return "Converts a value to uppercase text"


class TrimFunction(BaseFunction):
    """Trim leading/trailing spaces from text."""

    @property
    def name(self) -> str:
        return "trim"

    def execute(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @property
    def description(self) -> str:
        return "Removes leading and trailing whitespace"


class SplitFunction(BaseFunction):
    """Split text into an array using a separator."""

    @property
    def name(self) -> str:
        return "split"

    def execute(self, value: Any, separator: Any) -> list:
        if value is None:
            return []

        text = str(value)
        sep = "" if separator is None else str(separator)

        if sep == "":
            return list(text)
        return text.split(sep)

    @property
    def description(self) -> str:
        return "Splits a string by separator and returns an array"


class JoinFunction(BaseFunction):
    """Join array items into a string with a separator."""

    @property
    def name(self) -> str:
        return "join"

    def execute(self, value: Any, separator: Any) -> str:
        if value is None:
            return ""

        if not isinstance(value, list):
            return str(value)

        sep = "" if separator is None else str(separator)
        return sep.join(str(item) for item in value)

    @property
    def description(self) -> str:
        return "Joins array elements into a string using separator"


class FlattenFunction(BaseFunction):
    """Recursively flatten nested arrays."""

    @property
    def name(self) -> str:
        return "flatten"

    def _flatten(self, value: list) -> list:
        result = []
        for item in value:
            if isinstance(item, list):
                result.extend(self._flatten(item))
            else:
                result.append(item)
        return result

    def execute(self, value: Any) -> list:
        if value is None:
            return []
        if not isinstance(value, list):
            return [value]
        return self._flatten(value)

    @property
    def description(self) -> str:
        return "Recursively flattens nested arrays"


class AllFunction(BaseFunction):
    """Return true when all elements are truthy."""

    @property
    def name(self) -> str:
        return "all"

    def execute(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, list):
            return all(value)
        return bool(value)

    @property
    def description(self) -> str:
        return "Returns true if all array elements are truthy"


class AnyFunction(BaseFunction):
    """Return true when at least one element is truthy."""

    @property
    def name(self) -> str:
        return "any"

    def execute(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, list):
            return any(value)
        return bool(value)

    @property
    def description(self) -> str:
        return "Returns true if any array element is truthy"


class FloorFunction(BaseFunction):
    """Apply floor operation to a numeric value."""

    @property
    def name(self) -> str:
        return "floor"

    def execute(self, value: Any) -> int:
        try:
            return math.floor(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"floor() expected a numeric argument, got: {value}") from exc

    @property
    def description(self) -> str:
        return "Rounds a number down to the nearest integer"


class CeilingFunction(BaseFunction):
    """Apply ceiling operation to a numeric value."""

    @property
    def name(self) -> str:
        return "ceiling"

    def execute(self, value: Any) -> int:
        try:
            return math.ceil(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"ceiling() expected a numeric argument, got: {value}"
            ) from exc

    @property
    def description(self) -> str:
        return "Rounds a number up to the nearest integer"


class MinFunction(BaseFunction):
    """Return the minimum numeric value from arguments."""

    @property
    def name(self) -> str:
        return "min"

    @staticmethod
    def _normalize_values(values: tuple[Any, ...]) -> list[Any]:
        """Support both variadic args and a single list argument."""
        if len(values) == 1 and isinstance(values[0], list):
            if not values[0]:
                raise ValueError("min() expects at least one value")
            return values[0]
        return list(values)

    def execute(self, *values: Any) -> Union[int, float]:
        if not values:
            raise ValueError("min() expects at least one argument")

        source_values = self._normalize_values(values)
        numbers = []
        for value in source_values:
            try:
                numbers.append(float(value))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"min() expected numeric arguments, got: {value}"
                ) from exc

        result = min(numbers)
        return int(result) if result.is_integer() else result

    @property
    def description(self) -> str:
        return "Returns the minimum value from numeric arguments"


class MaxFunction(BaseFunction):
    """Return the maximum numeric value from arguments."""

    @property
    def name(self) -> str:
        return "max"

    @staticmethod
    def _normalize_values(values: tuple[Any, ...]) -> list[Any]:
        """Support both variadic args and a single list argument."""
        if len(values) == 1 and isinstance(values[0], list):
            if not values[0]:
                raise ValueError("max() expects at least one value")
            return values[0]
        return list(values)

    def execute(self, *values: Any) -> Union[int, float]:
        if not values:
            raise ValueError("max() expects at least one argument")

        source_values = self._normalize_values(values)
        numbers = []
        for value in source_values:
            try:
                numbers.append(float(value))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"max() expected numeric arguments, got: {value}"
                ) from exc

        result = max(numbers)
        return int(result) if result.is_integer() else result

    @property
    def description(self) -> str:
        return "Returns the maximum value from numeric arguments"


# Registry of all built-in functions
BUILTIN_FUNCTIONS = [
    SizeFunction(),
    StringFunction(),
    NumberFunction(),
    BooleanFunction(),
    RoundFunction(),
    LowercaseFunction(),
    UppercaseFunction(),
    TrimFunction(),
    SplitFunction(),
    JoinFunction(),
    FlattenFunction(),
    AllFunction(),
    AnyFunction(),
    FloorFunction(),
    CeilingFunction(),
    MinFunction(),
    MaxFunction(),
]
