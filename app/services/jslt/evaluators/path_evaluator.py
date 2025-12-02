"""Evaluator for path expressions (property access)."""
import re
from typing import Any, Dict, Optional
from .base_evaluator import BaseEvaluator


class PathEvaluator(BaseEvaluator):
    """Evaluator for path expressions like .field or .array[0]."""

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

        # Handle path with array indexing
        while path:
            # Check for array indexing
            array_match = re.match(r"^([^.\[]+)\[(\d+)\](.*)$", path)
            if array_match:
                field_name, index_str, remaining = array_match.groups()

                # Get the field
                if isinstance(current, dict):
                    current = current.get(field_name)
                    if current is None:
                        return None
                else:
                    return None

                # Apply array index
                index = int(index_str)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return None

                # Continue with remaining path
                path = remaining.lstrip(".")
                continue

            # Check for field access
            dot_pos = path.find(".")
            bracket_pos = path.find("[")

            if dot_pos == -1 and bracket_pos == -1:
                # Last field
                if isinstance(current, dict):
                    return current.get(path)
                else:
                    return None

            # Find next separator
            next_sep = float("inf")
            if dot_pos != -1:
                next_sep = min(next_sep, dot_pos)
            if bracket_pos != -1:
                next_sep = min(next_sep, bracket_pos)

            if next_sep == float("inf"):
                # Single field remaining
                if isinstance(current, dict):
                    return current.get(path)
                else:
                    return None

            # Extract field name up to next separator
            field_name = path[:next_sep]
            if isinstance(current, dict):
                current = current.get(field_name)
                if current is None:
                    return None
            else:
                return None

            # Update path
            if next_sep == dot_pos:
                path = path[dot_pos + 1:]
            else:
                path = path[bracket_pos:]

        return current

    @property
    def priority(self) -> int:
        """Return priority for path evaluation."""
        return 50
