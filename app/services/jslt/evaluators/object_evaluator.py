"""Evaluator for object construction."""
from typing import Any, Dict, Optional, TYPE_CHECKING
from .base_evaluator import BaseEvaluator
from ..utils.expression_parser import ExpressionParser

if TYPE_CHECKING:
    from ..jslt_service import JSLTService


class ObjectEvaluator(BaseEvaluator):
    """Evaluator for object construction expressions."""

    def __init__(self, service: "JSLTService"):
        """
        Initialize the object evaluator.

        Args:
            service: Reference to the main JSLT service for recursive evaluation
        """
        self.service = service

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is an object construction."""
        return expression.startswith("{") and expression.endswith("}")

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Evaluate object construction."""
        if variables is None:
            variables = {}

        content = expression[1:-1].strip()
        if not content:
            return {}

        result = {}
        pairs = ExpressionParser.split_object_pairs(content)

        for pair in pairs:
            if ":" not in pair:
                raise ValueError(f"Invalid object pair: {pair}")

            key_part, value_part = pair.split(":", 1)
            key = key_part.strip()

            # Remove quotes from key if present
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            elif key.startswith("'") and key.endswith("'"):
                key = key[1:-1]

            # Use the main service to evaluate the value expression
            value = self.service._evaluate_expression(
                value_part.strip(), context, variables
            )
            result[key] = value

        return result

    @property
    def priority(self) -> int:
        """Return priority for object evaluation."""
        return 70
