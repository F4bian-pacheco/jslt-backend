"""Evaluator for array construction."""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from .base_evaluator import BaseEvaluator
from ..utils.expression_parser import ExpressionParser

if TYPE_CHECKING:
    from ..jslt_service import JSLTService


class ArrayEvaluator(BaseEvaluator):
    """Evaluator for array construction expressions."""

    def __init__(self, service: "JSLTService"):
        """
        Initialize the array evaluator.

        Args:
            service: Reference to the main JSLT service for recursive evaluation
        """
        self.service = service

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is an array construction."""
        # Check if it's an array but NOT a for loop (which also uses brackets)
        if not (expression.startswith("[") and expression.endswith("]")):
            return False

        # If it starts with [for, it should be handled by ControlFlowEvaluator
        content = expression[1:-1].strip()
        if content.startswith("for"):
            return False

        return True

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """Evaluate array construction."""
        if variables is None:
            variables = {}

        content = expression[1:-1].strip()
        if not content:
            return []

        elements = ExpressionParser.split_array_elements(content)
        return [
            self.service._evaluate_expression(elem.strip(), context, variables)
            for elem in elements
        ]

    @property
    def priority(self) -> int:
        """Return priority for array evaluation."""
        return 70
