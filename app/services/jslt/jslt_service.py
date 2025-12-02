"""Refactored JSLT service using evaluator pattern."""
import time
from typing import Any, Dict, List, Optional
from app.models.transform import TransformResponse, JSLTValidationResponse

from .evaluators import (
    BaseEvaluator,
    LiteralEvaluator,
    PathEvaluator,
    ObjectEvaluator,
    ArrayEvaluator,
    VariableEvaluator,
    OperatorEvaluator,
    ControlFlowEvaluator,
    FunctionEvaluator,
)
from .functions import BUILTIN_FUNCTIONS, BaseFunction


class JSLTService:
    """Custom JSLT interpreter for JSON transformations using the evaluator pattern."""

    def __init__(self):
        """Initialize the JSLT service with evaluators and functions."""
        self.variables = {}  # Global variable context
        self.functions: Dict[str, BaseFunction] = {}
        self.evaluators: List[BaseEvaluator] = []

        # Register built-in functions
        self._register_builtin_functions()

        # Initialize evaluators (order doesn't matter as we use priority)
        self._initialize_evaluators()

    def _register_builtin_functions(self):
        """Register all built-in functions."""
        for func in BUILTIN_FUNCTIONS:
            self.register_function(func)

    def _initialize_evaluators(self):
        """Initialize all evaluators and sort by priority."""
        # Create evaluators that need service reference
        self.evaluators = [
            VariableEvaluator(self),
            ControlFlowEvaluator(self),
            OperatorEvaluator(self),
            ObjectEvaluator(self),
            ArrayEvaluator(self),
            FunctionEvaluator(self),
            PathEvaluator(),
            LiteralEvaluator(),
        ]

        # Sort evaluators by priority (highest first)
        self.evaluators.sort(key=lambda e: e.priority, reverse=True)

    def register_function(self, func: BaseFunction):
        """
        Register a custom function.

        Args:
            func: The function to register
        """
        self.functions[func.name] = func

    def register_evaluator(self, evaluator: BaseEvaluator):
        """
        Register a custom evaluator.

        Args:
            evaluator: The evaluator to register
        """
        self.evaluators.append(evaluator)
        # Re-sort evaluators by priority
        self.evaluators.sort(key=lambda e: e.priority, reverse=True)

    def transform(
        self, input_json: Dict[str, Any], jslt_expression: str
    ) -> TransformResponse:
        """
        Transform JSON using JSLT expression.

        Args:
            input_json: Input JSON data
            jslt_expression: JSLT transformation expression

        Returns:
            TransformResponse with the result
        """
        start_time = time.perf_counter()

        try:
            # Reset variables for each transform
            self.variables = {}
            result = self._evaluate_expression(
                jslt_expression.strip(), input_json, {})
            execution_time = (time.perf_counter() - start_time) * 1000

            return TransformResponse(
                success=True, output=result, execution_time_ms=round(execution_time, 3)
            )
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            return TransformResponse(
                success=False, error=str(e), execution_time_ms=round(execution_time, 3)
            )

    def validate_jslt(self, jslt_expression: str) -> JSLTValidationResponse:
        """
        Validate JSLT expression syntax.

        Args:
            jslt_expression: JSLT expression to validate

        Returns:
            JSLTValidationResponse with validation result
        """
        try:
            # Try to parse the expression with a comprehensive dummy input
            test_input = {
                "test": "value",
                "array": [1, 2, 3],
                "name": "John Doe",
                "age": 25,
                "city": "New York",
                "skills": ["JavaScript", "Python", "Java"]
            }
            self.variables = {}  # Reset variables for validation
            self._evaluate_expression(jslt_expression.strip(), test_input, {})
            return JSLTValidationResponse(valid=True)
        except Exception as e:
            return JSLTValidationResponse(
                valid=False, error=str(e), suggestions=self._get_suggestions(str(e))
            )

    def _evaluate_expression(
        self, expression: str, context: Any, variables: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Evaluate a JSLT expression in the given context using the chain of evaluators.

        Args:
            expression: The JSLT expression to evaluate
            context: The current context (JSON data)
            variables: Dictionary of variables available in the current scope

        Returns:
            The result of evaluating the expression

        Raises:
            ValueError: If the expression cannot be evaluated
        """
        if variables is None:
            variables = {}

        expression = expression.strip()

        if not expression:
            return None

        # Handle multi-line expressions with let statements
        if "let " in expression and "\n" in expression:
            return self._evaluate_multiline_expression(expression, context, variables)

        # Try each evaluator in priority order
        for evaluator in self.evaluators:
            if evaluator.can_evaluate(expression, context):
                return evaluator.evaluate(expression, context, variables)

        # If no evaluator can handle it, raise an error
        raise ValueError(f"Invalid expression: {expression}")

    def _evaluate_multiline_expression(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Any:
        """
        Evaluate multi-line expression with let statements.

        Args:
            expression: The multi-line JSLT expression
            context: The current context
            variables: Dictionary of variables

        Returns:
            The result of evaluating the expression
        """
        import re

        lines = expression.split('\n')
        current_variables = variables.copy()

        # Process let statements first
        let_statements = []
        object_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("let "):
                let_statements.append(line)
            elif line:
                object_lines.append(line)

        # Evaluate let statements
        for let_stmt in let_statements:
            let_match = re.match(r"^let\s+(\w+)\s*=\s*(.+)$", let_stmt)
            if let_match:
                var_name, value_expr = let_match.groups()
                value = self._evaluate_expression(
                    value_expr.strip(), context, current_variables)
                current_variables[var_name] = value

        # Evaluate the remaining expression (usually an object)
        remaining_expr = '\n'.join(object_lines)
        if remaining_expr:
            return self._evaluate_expression(remaining_expr, context, current_variables)

        return None

    def _get_suggestions(self, error_msg: str) -> List[str]:
        """
        Get suggestions based on error message.

        Args:
            error_msg: The error message

        Returns:
            List of helpful suggestions
        """
        suggestions = []

        if "Unknown function" in error_msg:
            available_functions = ", ".join(
                [f"{name}()" for name in self.functions.keys()])
            suggestions.append(f"Available functions: {available_functions}")

        if "Invalid expression" in error_msg:
            suggestions.extend([
                "Use .field to access object properties",
                "Use .array[0] to access array elements",
                "Use {} for object construction",
                "Use [] for array construction",
            ])

        return suggestions
