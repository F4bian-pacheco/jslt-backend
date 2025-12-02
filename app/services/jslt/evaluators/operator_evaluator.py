"""Evaluator for operator expressions (comparison, addition, etc.)."""
from typing import Any, Dict, Optional, Union, TYPE_CHECKING
from .base_evaluator import BaseEvaluator
from ..utils.expression_parser import ExpressionParser

if TYPE_CHECKING:
    from ..jslt_service import JSLTService


class OperatorEvaluator(BaseEvaluator):
    """Evaluator for operator expressions."""

    def __init__(self, service: "JSLTService"):
        """
        Initialize the operator evaluator.

        Args:
            service: Reference to the main JSLT service for recursive evaluation
        """
        self.service = service

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is an operator expression."""
        # Don't evaluate if it starts with object/array construction
        if expression.startswith("{") or expression.startswith("["):
            return False

        # Don't evaluate if it's a control flow expression
        if expression.startswith("if") or expression.startswith("for"):
            return False

        # Check for comparison operators at the top level
        if self._has_top_level_operator(expression, [" >= ", " <= ", " > ", " < ", " == ", " != "]):
            return True

        # Check for addition operator at the top level
        if self._has_top_level_operator(expression, [" + "]):
            return True

        return False

    def _has_top_level_operator(self, expression: str, operators: list) -> bool:
        """Check if the expression has an operator at the top level (not inside nested structures)."""
        depth = 0
        in_string = False
        string_char = None

        for i, char in enumerate(expression):
            if not in_string and char in '"\'':
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
            elif not in_string:
                if char in "{[(":
                    depth += 1
                elif char in "}])":
                    depth -= 1
                elif depth == 0:
                    # Check if any operator matches at this position
                    for op in operators:
                        if expression[i:i+len(op)] == op:
                            return True

        return False

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Evaluate operator expressions."""
        if variables is None:
            variables = {}

        # Handle comparison operations (check longer operators first)
        if " >= " in expression:
            return self._evaluate_comparison(expression, context, ">=", variables)
        if " <= " in expression:
            return self._evaluate_comparison(expression, context, "<=", variables)
        if " > " in expression:
            return self._evaluate_comparison(expression, context, ">", variables)
        if " < " in expression:
            return self._evaluate_comparison(expression, context, "<", variables)
        if " == " in expression:
            return self._evaluate_comparison(expression, context, "==", variables)
        if " != " in expression:
            return self._evaluate_comparison(expression, context, "!=", variables)

        # Handle string/number concatenation/addition
        if " + " in expression:
            return self._evaluate_addition(expression, context, variables)

        raise ValueError(f"Invalid operator expression: {expression}")

    def _evaluate_comparison(
        self,
        expression: str,
        context: Any,
        operator: str,
        variables: Dict[str, Any],
    ) -> bool:
        """Evaluate comparison expression."""
        left_expr, right_expr = expression.split(f" {operator} ", 1)
        left_val = self.service._evaluate_expression(
            left_expr.strip(), context, variables
        )
        right_val = self.service._evaluate_expression(
            right_expr.strip(), context, variables
        )

        # Handle null/None values
        if operator == "==":
            return left_val == right_val
        elif operator == "!=":
            return left_val != right_val

        # For ordering operators, treat None as falsy in comparisons
        if left_val is None or right_val is None:
            return False

        # Both values are not None, proceed with comparison
        try:
            if operator == ">=":
                return left_val >= right_val
            elif operator == "<=":
                return left_val <= right_val
            elif operator == ">":
                return left_val > right_val
            elif operator == "<":
                return left_val < right_val
        except TypeError:
            # If types are incompatible for comparison, return False
            return False

        return False

    def _evaluate_addition(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Union[str, int, float]:
        """Evaluate addition/concatenation expression."""
        # Split by " + " but be careful with nested expressions
        parts = ExpressionParser.split_addition_parts(expression)
        if len(parts) == 1:
            return self.service._evaluate_expression(
                parts[0].strip(), context, variables
            )

        # Evaluate all parts
        values = []
        for part in parts:
            val = self.service._evaluate_expression(
                part.strip(), context, variables
            )
            values.append(val)

        # If any value is a string, do string concatenation
        if any(isinstance(v, str) for v in values):
            result = ""
            for val in values:
                result += str(val if val is not None else "")
            return result

        # If all are numbers, do numeric addition
        if all(isinstance(v, (int, float)) for v in values if v is not None):
            result = 0
            for val in values:
                if val is not None:
                    result += val
            return result

        # Default: string concatenation
        result = ""
        for val in values:
            result += str(val if val is not None else "")
        return result

    @property
    def priority(self) -> int:
        """Return priority for operator evaluation."""
        return 80
