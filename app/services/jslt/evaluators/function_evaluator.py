"""Evaluator for function calls."""
import re
from typing import Any, Dict, Optional, TYPE_CHECKING
from .base_evaluator import BaseEvaluator
from ..utils.expression_parser import ExpressionParser

if TYPE_CHECKING:
    from ..jslt_service import JSLTService


class FunctionEvaluator(BaseEvaluator):
    """Evaluator for function call expressions."""

    def __init__(self, service: "JSLTService"):
        """
        Initialize the function evaluator.

        Args:
            service: Reference to the main JSLT service for recursive evaluation
        """
        self.service = service

    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if the expression is a function call."""
        func_match = re.match(r"^(\w+)\s*\(([^)]*)\)$", expression)
        return func_match is not None

    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Evaluate function calls."""
        if variables is None:
            variables = {}

        func_match = re.match(r"^(\w+)\s*\(([^)]*)\)$", expression)
        if not func_match:
            raise ValueError(f"Invalid function call: {expression}")

        func_name, args_str = func_match.groups()

        if func_name not in self.service.functions:
            raise ValueError(f"Unknown function: {func_name}")

        args = []
        if args_str.strip():
            arg_expressions = ExpressionParser.split_function_args(args_str)
            args = [
                self.service._evaluate_expression(arg.strip(), context, variables)
                for arg in arg_expressions
            ]

        func = self.service.functions[func_name]
        return func.execute(*args)

    @property
    def priority(self) -> int:
        """Return priority for function evaluation."""
        return 60
