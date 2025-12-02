"""Evaluator for variable references and let statements."""
import re
from typing import Any, Dict, Optional, TYPE_CHECKING
from .base_evaluator import BaseEvaluator
from ..utils.expression_parser import ExpressionParser

if TYPE_CHECKING:
    from ..jslt_service import JSLTService


class VariableEvaluator(BaseEvaluator):
    """Evaluator for variable references and let statements."""

    def __init__(self, service: "JSLTService"):
        """
        Initialize the variable evaluator.

        Args:
            service: Reference to the main JSLT service for recursive evaluation
        """
        self.service = service

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is a variable reference or let statement."""
        return expression.startswith("$") or expression.startswith("let ")

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Evaluate variable references and let statements."""
        if variables is None:
            variables = {}

        # Handle variable references
        if expression.startswith("$"):
            return self._evaluate_variable_reference(expression, variables)

        # Handle let statements
        if expression.startswith("let "):
            return self._evaluate_let_statement(expression, context, variables)

        raise ValueError(f"Invalid variable expression: {expression}")

    def _evaluate_variable_reference(
        self, expression: str, variables: Dict[str, Any]
    ) -> Any:
        """Evaluate variable reference like $varName."""
        # Extract just the variable name (up to first non-alphanumeric character)
        var_match = re.match(r"^\$(\w+)", expression)
        if var_match:
            var_name = var_match.group(1)
            if var_name in variables:
                return variables[var_name]
            elif var_name in self.service.variables:
                return self.service.variables[var_name]
            else:
                raise ValueError(f"Undefined variable: ${var_name}")
        else:
            raise ValueError(f"Invalid variable reference: {expression}")

    def _evaluate_let_statement(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Any:
        """Evaluate let statement and return the rest of the expression."""
        # Check for "let var = value in expression" syntax first
        in_match = re.match(
            r"^let\s+(\w+)\s*=\s*(.+?)\s+in\s+(.+)$", expression, re.DOTALL
        )
        if in_match:
            var_name, value_expr, rest_expr = in_match.groups()

            # Evaluate the value expression
            value = self.service._evaluate_expression(
                value_expr.strip(), context, variables
            )

            # Store in local variables (takes precedence over global)
            new_variables = variables.copy()
            new_variables[var_name] = value

            # Evaluate the rest expression with the new variable
            return self.service._evaluate_expression(
                rest_expr.strip(), context, new_variables
            )

        # Fallback to the original approach for backward compatibility
        let_match = re.match(r"^let\s+(\w+)\s*=\s*", expression)
        if not let_match:
            raise ValueError(
                "Invalid let syntax. Use: let variable = expression in expression"
            )

        var_name = let_match.group(1)
        after_equals = expression[let_match.end():]

        # Find where the value expression ends
        value_expr, rest_expr = ExpressionParser.split_let_expression(after_equals)

        # Evaluate the value expression
        value = self.service._evaluate_expression(
            value_expr.strip(), context, variables
        )

        # Store in local variables (takes precedence over global)
        new_variables = variables.copy()
        new_variables[var_name] = value

        # If there's more expression after the let, evaluate it with the new variable
        if rest_expr and rest_expr.strip():
            return self.service._evaluate_expression(
                rest_expr.strip(), context, new_variables
            )

        # If it's just a let statement, return the value
        return value

    @property
    def priority(self) -> int:
        """Return priority for variable evaluation."""
        return 100
