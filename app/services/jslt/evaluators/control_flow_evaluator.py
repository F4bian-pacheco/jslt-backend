"""Evaluator for control flow expressions (if, for)."""

import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from .base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from ..jslt_service import JSLTService


class ControlFlowEvaluator(BaseEvaluator):
    """Evaluator for control flow expressions."""

    def __init__(self, service: "JSLTService"):
        """
        Initialize the control flow evaluator.

        Args:
            service: Reference to the main JSLT service for recursive evaluation
        """
        self.service = service

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is a control flow expression."""
        # Check for if expressions
        if expression.startswith("if"):
            return True

        # Check for for expressions (can be either "for ..." or "[for ...]")
        if expression.startswith("for"):
            return True

        # Check for array-based for loops: [for (...) ...]
        if expression.startswith("[") and expression.endswith("]"):
            content = expression[1:-1].strip()
            if content.startswith("for"):
                return True

        return False

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Evaluate control flow expressions."""
        if variables is None:
            variables = {}

        if expression.startswith("if"):
            return self._evaluate_if_expression(expression, context, variables)
        elif expression.startswith("for"):
            return self._evaluate_for_loop(expression, context, variables)
        elif expression.startswith("[") and expression.endswith("]"):
            # Handle [for ...] syntax
            content = expression[1:-1].strip()
            if content.startswith("for"):
                return self._evaluate_for_loop(content, context, variables)

        raise ValueError(f"Invalid control flow expression: {expression}")

    def _evaluate_if_expression(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Any:
        """
        Evaluate if-then-else expression.

        Syntax: if (condition) then_expr [else else_expr]

        The else clause is optional. If omitted and condition is false, returns null.

        Falsy values: false, null, {} (empty objects), [] (empty arrays)
        Everything else is truthy.
        """
        # Try to match with else clause first
        match = re.match(
            r"if\s*\(\s*([^)]+)\s*\)\s*(.+?)\s+else\s+(.+)", expression, re.DOTALL
        )

        if match:
            # if-else syntax
            condition_expr, then_expr, else_expr = match.groups()
        else:
            # Try to match without else clause
            match = re.match(r"if\s*\(\s*([^)]+)\s*\)\s*(.+)", expression, re.DOTALL)
            if not match:
                raise ValueError("Invalid if expression syntax")
            condition_expr, then_expr = match.groups()
            else_expr = None

        # Evaluate condition
        condition = self.service._evaluate_expression(
            condition_expr.strip(), context, variables
        )

        # Check if condition is truthy according to JSLT rules
        # Falsy: false, null, {}, []
        is_truthy = self._is_truthy(condition)

        if is_truthy:
            return self.service._evaluate_expression(
                then_expr.strip(), context, variables
            )
        else:
            if else_expr is not None:
                return self.service._evaluate_expression(
                    else_expr.strip(), context, variables
                )
            else:
                # No else clause - return null
                return None

    def _is_truthy(self, value: Any) -> bool:
        """
        Determine if a value is truthy according to JSLT rules.

        Falsy values:
        - boolean false
        - null
        - {} (empty objects)
        - [] (empty arrays)

        Everything else is truthy.
        """
        if value is None or value is False:
            return False
        if isinstance(value, dict) and len(value) == 0:
            return False
        if isinstance(value, list) and len(value) == 0:
            return False
        return True

    def _evaluate_for_loop(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> List[Any]:
        """Evaluate for loop expression."""
        # Pattern: for (array_expr) loop_expr
        match = re.match(r"for\s*\(\s*([^)]+)\s*\)\s*(.+)", expression)
        if not match:
            raise ValueError("Invalid for loop syntax")

        array_expr, loop_expr = match.groups()
        array_value = self.service._evaluate_expression(
            array_expr.strip(), context, variables
        )

        if not isinstance(array_value, list):
            raise ValueError("For loop requires an array")

        results = []
        for item in array_value:
            result = self.service._evaluate_expression(
                loop_expr.strip(), item, variables
            )
            results.append(result)

        return results

    @property
    def priority(self) -> int:
        """Return priority for control flow evaluation."""
        return 90
