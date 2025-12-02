"""Evaluator for literal values (strings, numbers, booleans, null)."""
from typing import Any, Dict, Optional
from .base_evaluator import BaseEvaluator
from ..utils.expression_parser import ExpressionParser


class LiteralEvaluator(BaseEvaluator):
    """Evaluator for literal values."""

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is a literal value."""
        return (
            ExpressionParser.is_string_literal(expression)
            or ExpressionParser.is_number_literal(expression)
            or ExpressionParser.is_boolean_literal(expression)
            or ExpressionParser.is_null_literal(expression)
        )

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Evaluate literal values."""
        # String literals
        if ExpressionParser.is_string_literal(expression):
            return expression[1:-1]

        # Number literals
        if ExpressionParser.is_number_literal(expression):
            return float(expression) if "." in expression else int(expression)

        # Boolean literals
        if expression == "true":
            return True
        if expression == "false":
            return False

        # Null literal
        if expression == "null":
            return None

        raise ValueError(f"Invalid literal expression: {expression}")

    @property
    def priority(self) -> int:
        """Return priority for literal evaluation."""
        return 40
