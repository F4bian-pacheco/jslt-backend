"""Evaluator for path expressions (property access)."""
from typing import Any, Dict, Optional
from .base_evaluator import BaseEvaluator


class PathEvaluator(BaseEvaluator):
    """Evaluator for path expressions like .field or .array[0]."""

    @staticmethod
    def _parse_optional_int(value: str) -> Optional[int]:
        """Parse optional integer values used in slices."""
        value = value.strip()
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def _apply_bracket_access(current: Any, token: str) -> Any:
        """Apply index or slice access to a list value."""
        if not isinstance(current, list):
            return None

        token = token.strip()
        if ":" in token:
            # Array slicing: [start:end], [:end], [start:], [-3:-1]
            parts = token.split(":")
            if len(parts) != 2:
                return None

            start = PathEvaluator._parse_optional_int(parts[0])
            end = PathEvaluator._parse_optional_int(parts[1])

            if (parts[0].strip() and start is None) or (parts[1].strip() and end is None):
                return None

            return current[slice(start, end)]

        # Single index access: supports negative indexing
        try:
            index = int(token)
        except ValueError:
            return None

        if -len(current) <= index < len(current):
            return current[index]
        return None

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is a path expression."""
        return expression.startswith(".")

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Evaluate path expressions."""
        if expression == ".":
            return context

        path = expression[1:]  # Remove leading dot
        current = context

        while path:
            if path.startswith("."):
                path = path[1:]
                continue

            # Parse field name if present (up to next dot or bracket)
            field_name = ""
            idx = 0
            while idx < len(path) and path[idx] not in ".[":
                field_name += path[idx]
                idx += 1

            if field_name:
                if not isinstance(current, dict):
                    return None
                current = current.get(field_name)
                if current is None:
                    return None
                path = path[idx:]

            # Apply one or more bracket operations: [0], [-1], [1:3], etc.
            while path.startswith("["):
                close_idx = path.find("]")
                if close_idx == -1:
                    return None

                token = path[1:close_idx]
                current = self._apply_bracket_access(current, token)
                if current is None:
                    return None

                path = path[close_idx + 1:]

            # If no field or bracket was consumed and we are still not moving,
            # the path is malformed.
            if not field_name and not path.startswith(".") and not path.startswith("["):
                return None

        return current

    @property
    def priority(self) -> int:
        """Return priority for path evaluation."""
        return 50
