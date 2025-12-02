"""Evaluator for operator expressions (comparison, addition, etc.)."""

from typing import Any, Dict, Optional, Union, TYPE_CHECKING
from .base_evaluator import BaseEvaluator

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
        if self._has_top_level_operator(
            expression, [" >= ", " <= ", " > ", " < ", " == ", " != "]
        ):
            return True

        # Check for arithmetic operators at the top level
        if self._has_top_level_operator(
            expression, [" + ", " - ", " * ", " / ", " % "]
        ):
            return True

        return False

    def _has_top_level_operator(self, expression: str, operators: list) -> bool:
        """Check if the expression has an operator at the top level (not inside nested structures)."""
        depth = 0
        in_string = False
        string_char = None

        for i, char in enumerate(expression):
            if not in_string and char in "\"'":
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
                        if expression[i : i + len(op)] == op:
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

        # Handle arithmetic operations
        # Check if we have additive operators (lower precedence)
        # If so, we need to handle precedence correctly
        if self._has_top_level_operator(expression, [" + ", " - "]):
            return self._evaluate_additive(expression, context, variables)

        # Otherwise, check for multiplicative operators (higher precedence)
        if " * " in expression or " / " in expression or " % " in expression:
            return self._evaluate_multiplicative(expression, context, variables)

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

    def _evaluate_multiplicative(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Union[int, float]:
        """Evaluate multiplicative operations (*, /, %)."""
        # Process left to right for operators of same precedence
        result = None
        current_expr = ""
        current_op = None

        i = 0
        while i < len(expression):
            # Check for operators
            if i < len(expression) - 2:
                op_check = expression[i : i + 3]
                if op_check in [" * ", " / ", " % "]:
                    # Evaluate the accumulated expression
                    if current_expr:
                        val = self.service._evaluate_expression(
                            current_expr.strip(), context, variables
                        )
                        if result is None:
                            result = val
                        else:
                            # Apply the previous operator
                            if current_op == "*":
                                result = result * val
                            elif current_op == "/":
                                result = result / val if val != 0 else None
                            elif current_op == "%":
                                result = result % val if val != 0 else None

                    current_op = op_check.strip()
                    current_expr = ""
                    i += 3
                    continue

            current_expr += expression[i]
            i += 1

        # Evaluate the last part
        if current_expr:
            val = self.service._evaluate_expression(
                current_expr.strip(), context, variables
            )
            if result is None:
                result = val
            else:
                if current_op == "*":
                    result = result * val
                elif current_op == "/":
                    result = result / val if val != 0 else None
                elif current_op == "%":
                    result = result % val if val != 0 else None

        return result

    def _evaluate_additive(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Union[str, int, float]:
        """Evaluate additive operations (+, -)."""
        # Process left to right for operators of same precedence
        result = None
        current_expr = ""
        current_op = None
        is_string_concat = False

        i = 0
        while i < len(expression):
            # Check for operators
            if i < len(expression) - 2:
                op_check = expression[i : i + 3]
                if op_check in [" + ", " - "]:
                    # Evaluate the accumulated expression
                    # This might contain multiplicative operations
                    if current_expr:
                        expr_stripped = current_expr.strip()
                        # Check if it contains multiplicative operators
                        if any(op in expr_stripped for op in [" * ", " / ", " % "]):
                            val = self._evaluate_multiplicative(
                                expr_stripped, context, variables
                            )
                        else:
                            val = self.service._evaluate_expression(
                                expr_stripped, context, variables
                            )

                        # Check if we're doing string concatenation
                        if isinstance(val, str):
                            is_string_concat = True

                        if result is None:
                            result = val
                        else:
                            # Apply the previous operator
                            if is_string_concat:
                                # String concatenation
                                result = str(
                                    result if result is not None else ""
                                ) + str(val if val is not None else "")
                            else:
                                # Numeric operation
                                if current_op == "+":
                                    result = (result if result is not None else 0) + (
                                        val if val is not None else 0
                                    )
                                elif current_op == "-":
                                    result = (result if result is not None else 0) - (
                                        val if val is not None else 0
                                    )

                    current_op = op_check.strip()
                    current_expr = ""
                    i += 3
                    continue

            current_expr += expression[i]
            i += 1

        # Evaluate the last part
        if current_expr:
            expr_stripped = current_expr.strip()
            # Check if it contains multiplicative operators
            if any(op in expr_stripped for op in [" * ", " / ", " % "]):
                val = self._evaluate_multiplicative(expr_stripped, context, variables)
            else:
                val = self.service._evaluate_expression(
                    expr_stripped, context, variables
                )

            # Check if we're doing string concatenation
            if isinstance(val, str):
                is_string_concat = True

            if result is None:
                result = val
            else:
                if is_string_concat:
                    # String concatenation
                    result = str(result if result is not None else "") + str(
                        val if val is not None else ""
                    )
                else:
                    # Numeric operation
                    if current_op == "+":
                        result = (result if result is not None else 0) + (
                            val if val is not None else 0
                        )
                    elif current_op == "-":
                        result = (result if result is not None else 0) - (
                            val if val is not None else 0
                        )

        return result

    @property
    def priority(self) -> int:
        """Return priority for operator evaluation."""
        return 80
