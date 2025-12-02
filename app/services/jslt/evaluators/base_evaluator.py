"""Base evaluator class for JSLT expression evaluation."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseEvaluator(ABC):
    """Abstract base class for JSLT expression evaluators."""

    @abstractmethod
    def can_evaluate(self, expression: str, context: Any) -> bool:
        """
        Determine if this evaluator can handle the given expression.

        Args:
            expression: The JSLT expression to evaluate
            context: The current evaluation context

        Returns:
            True if this evaluator can handle the expression, False otherwise
        """
        pass

    @abstractmethod
    def evaluate(
        self,
        expression: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Evaluate the expression in the given context.

        Args:
            expression: The JSLT expression to evaluate
            context: The current evaluation context (JSON data)
            variables: Dictionary of variables available in the current scope

        Returns:
            The result of evaluating the expression

        Raises:
            ValueError: If the expression is invalid or cannot be evaluated
        """
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Return the priority of this evaluator.
        Higher priority evaluators are checked first.

        Priority guidelines:
        - 100: Variable references and let statements
        - 90: Control flow (if, for)
        - 80: Operators (comparison, addition)
        - 70: Object/Array construction
        - 60: Function calls
        - 50: Path expressions
        - 40: Literals (strings, numbers, booleans)

        Returns:
            Integer representing the priority
        """
        pass
