# JSLT Service Architecture

## Overview

The JSLT service has been refactored from a monolithic 760-line class into a modular, extensible architecture using the **Strategy Pattern** combined with **Chain of Responsibility**.

## Design Patterns

### 1. Strategy Pattern
Each evaluator is a strategy for handling a specific type of JSLT expression:

```python
class BaseEvaluator(ABC):
    @abstractmethod
    def can_evaluate(self, expression: str, context: Any) -> bool:
        """Check if this evaluator can handle the expression"""
        pass

    @abstractmethod
    def evaluate(self, expression: str, context: Any, variables: Dict) -> Any:
        """Evaluate the expression"""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Higher priority = evaluated first"""
        pass
```

### 2. Chain of Responsibility
Evaluators are tried in priority order until one can handle the expression:

```python
def _evaluate_expression(self, expression: str, context: Any, variables: Dict) -> Any:
    # Try each evaluator in priority order
    for evaluator in self.evaluators:
        if evaluator.can_evaluate(expression, context):
            return evaluator.evaluate(expression, context, variables)

    raise ValueError(f"Invalid expression: {expression}")
```

### 3. Template Method
Base classes define the structure, concrete classes implement the details:

```python
class BaseFunction(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, *args: Any) -> Any:
        pass
```

## Directory Structure

```
app/services/jslt/
├── __init__.py                    # Package exports
├── jslt_service.py                # Main orchestrator (199 lines, down from 760)
├── evaluators/                    # Expression evaluators
│   ├── __init__.py
│   ├── base_evaluator.py         # Abstract base class
│   ├── literal_evaluator.py      # Strings, numbers, booleans, null
│   ├── path_evaluator.py         # .field, .array[0], .nested.field
│   ├── object_evaluator.py       # { "key": value }
│   ├── array_evaluator.py        # [item1, item2]
│   ├── variable_evaluator.py     # let x = value, $x
│   ├── operator_evaluator.py     # >=, <, ==, +
│   ├── control_flow_evaluator.py # if, for
│   └── function_evaluator.py     # size(), string(), etc.
├── functions/                     # Function implementations
│   ├── __init__.py
│   ├── base_function.py          # Abstract base class
│   └── builtin_functions.py      # Built-in functions
└── utils/                         # Utilities
    ├── __init__.py
    └── expression_parser.py       # Parsing helpers
```

## Evaluator Priority System

Evaluators are processed in priority order (highest first):

| Priority | Evaluator | Handles |
|----------|-----------|---------|
| 100 | VariableEvaluator | `$var`, `let x = value` |
| 90 | ControlFlowEvaluator | `if`, `for` |
| 80 | OperatorEvaluator | `>=`, `<`, `+` |
| 70 | ObjectEvaluator | `{ "key": value }` |
| 70 | ArrayEvaluator | `[item1, item2]` |
| 60 | FunctionEvaluator | `size()`, `string()` |
| 50 | PathEvaluator | `.field`, `.array[0]` |
| 40 | LiteralEvaluator | `"string"`, `123`, `true` |

## Extensibility

### Adding a New Function

```python
from app.services.jslt.functions import BaseFunction

class UpperFunction(BaseFunction):
    @property
    def name(self) -> str:
        return "upper"

    def execute(self, value: str) -> str:
        return value.upper()

# Register
service = JSLTService()
service.register_function(UpperFunction())
```

### Adding a New Evaluator

```python
from app.services.jslt.evaluators import BaseEvaluator

class RegexEvaluator(BaseEvaluator):
    def can_evaluate(self, expression: str, context: Any) -> bool:
        return expression.startswith("regex(")

    def evaluate(self, expression: str, context: Any, variables: Dict) -> Any:
        # Extract pattern and text
        # Apply regex
        pass

    @property
    def priority(self) -> int:
        return 75  # Between operators and functions

# Register
service = JSLTService()
service.register_evaluator(RegexEvaluator(service))
```

## Benefits of Refactoring

### 1. Maintainability
- **Before**: 760 lines in one file
- **After**: Multiple focused modules, largest is ~150 lines

### 2. Testability
- Each evaluator can be tested independently
- Easier to mock dependencies
- Clear separation of concerns

### 3. Extensibility
- Add new features without modifying existing code (Open/Closed Principle)
- Register custom evaluators and functions at runtime
- Clear extension points through base classes

### 4. Readability
- Each file has a single, clear responsibility
- Easy to find and understand specific functionality
- Self-documenting structure

### 5. SOLID Principles
- ✅ **Single Responsibility**: Each evaluator handles one expression type
- ✅ **Open/Closed**: Open for extension, closed for modification
- ✅ **Liskov Substitution**: All evaluators are interchangeable
- ✅ **Interface Segregation**: Small, focused interfaces
- ✅ **Dependency Inversion**: Depend on abstractions, not concretions

## Migration Notes

### Backwards Compatibility
- The public API (`transform()` and `validate_jslt()`) remains unchanged
- All existing functionality is preserved
- Tests pass without modification

### Breaking Changes
- None - this is a pure refactoring

### Performance
- Similar performance to the original implementation
- Potential for future optimizations through evaluator caching
- Priority system ensures efficient evaluation order

## Future Enhancements

### Potential Additions
1. **Expression Caching**: Cache compiled expressions for repeated use
2. **Lazy Evaluation**: Defer evaluation until value is needed
3. **Async Support**: Async evaluators for I/O operations
4. **Plugin System**: Load evaluators from external modules
5. **DSL Builder**: Fluent API for building transformations

### Example: Expression Caching
```python
class JSLTService:
    def __init__(self):
        self._cache = {}

    def transform(self, input_json: Dict, jslt_expression: str) -> TransformResponse:
        # Check cache
        cache_key = hash(jslt_expression)
        if cache_key in self._cache:
            compiled = self._cache[cache_key]
        else:
            compiled = self._compile_expression(jslt_expression)
            self._cache[cache_key] = compiled

        # Execute cached/compiled expression
        result = compiled.execute(input_json)
        ...
```

## Testing Strategy

### Unit Tests
- Test each evaluator independently
- Mock the service for evaluators that need it
- Test edge cases and error conditions

### Integration Tests
- Test combinations of evaluators
- Test complex expressions
- Verify end-to-end functionality

### Example Test
```python
def test_variable_evaluator():
    service = JSLTService()
    evaluator = VariableEvaluator(service)

    # Test can_evaluate
    assert evaluator.can_evaluate("$var", {})
    assert evaluator.can_evaluate("let x = 5", {})
    assert not evaluator.can_evaluate(".field", {})

    # Test evaluate
    variables = {"x": 10}
    result = evaluator.evaluate("$x", {}, variables)
    assert result == 10
```

## References

- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
