# JSLT Playground Backend

FastAPI backend for the JSLT Playground - provides REST API endpoints for transforming JSON using JSLT expressions with custom variable support.

## Architecture

This backend follows Clean Architecture principles with clear separation of concerns and uses the **Strategy + Chain of Responsibility** pattern for the JSLT interpreter:

```
backend/
├── app/
│   ├── api/              # REST API endpoints
│   ├── core/             # Configuration and settings
│   ├── models/           # Pydantic models and schemas
│   ├── services/
│   │   └── jslt/         # Refactored JSLT interpreter (modular design)
│   │       ├── evaluators/    # Expression evaluators (Strategy pattern)
│   │       ├── functions/     # Built-in and custom functions
│   │       ├── utils/         # Parsing utilities
│   │       └── jslt_service.py # Main orchestrator
│   └── main.py           # FastAPI application setup
├── tests/                # Unit and integration tests
├── start.py              # Application entry point
└── requirements.txt      # Python dependencies
```

## Features

- **Custom JSLT Interpreter**: Full implementation of core JSLT features
- **Variable Support**: `let` statements and `$variable` references with proper scoping
- **RESTful API**: Transform and validation endpoints
- **Real-time Processing**: Fast JSON transformation and validation
- **CORS Support**: Configured for frontend integration
- **Error Handling**: Comprehensive error messages and suggestions
- **Clean Architecture**: Organized codebase for maintainability

## API Endpoints

### POST `/api/v1/transform`
Transform JSON data using JSLT expressions.

**Request:**
```json
{
  "input_json": {
    "name": "John",
    "age": 30,
    "skills": ["JavaScript", "Python"]
  },
  "jslt_expression": "let skillCount = size(.skills) { \"name\": .name, \"isAdult\": .age >= 18, \"skillCount\": $skillCount }"
}
```

**Response:**
```json
{
  "success": true,
  "output": {
    "name": "John",
    "isAdult": true,
    "skillCount": 2
  },
  "execution_time_ms": 1.23
}
```

### POST `/api/v1/validate`
Validate JSLT expression syntax.

**Request:**
```json
{
  "jslt_expression": "let x = .value { \"result\": $x }"
}
```

**Response:**
```json
{
  "valid": true,
  "error": null,
  "suggestions": []
}
```

## JSLT Service Features

The custom JSLT interpreter uses a modular, extensible architecture with the following components:

### 🏗️ Modular Architecture

#### **Evaluators (Strategy Pattern)**
Each evaluator handles a specific type of JSLT expression:
- **LiteralEvaluator**: String, number, boolean, and null literals
- **PathEvaluator**: Property access (`.field`, `.array[0]`, `.nested.field`)
- **ObjectEvaluator**: Object construction (`{ "key": .value }`)
- **ArrayEvaluator**: Array construction (`[.item1, .item2]`)
- **VariableEvaluator**: Variable declarations and references (`let x = .value`, `$x`)
- **OperatorEvaluator**: Comparisons and arithmetic (`>=`, `+`, etc.)
- **ControlFlowEvaluator**: Conditionals and loops (`if`, `for`)
- **FunctionEvaluator**: Function calls (`size()`, `string()`, etc.)

#### **Built-in Functions**
- `size(array)` - Get array/object/string length
- `string(value)` - Convert to string
- `number(value)` - Convert to number
- `boolean(value)` - Convert to boolean
- `round(number)` - Round to nearest integer

### 🔌 Extensibility

The service is designed for easy extension:

**Adding a Custom Function:**
```python
from app.services.jslt import JSLTService, BaseFunction

class UpperFunction(BaseFunction):
    @property
    def name(self) -> str:
        return "upper"

    def execute(self, value: str) -> str:
        return value.upper()

# Register the function
service = JSLTService()
service.register_function(UpperFunction())
```

**Adding a Custom Evaluator:**
```python
from app.services.jslt import JSLTService, BaseEvaluator

class CustomEvaluator(BaseEvaluator):
    def can_evaluate(self, expression: str, context: Any) -> bool:
        return expression.startswith("custom:")

    def evaluate(self, expression: str, context: Any, variables: Dict) -> Any:
        # Custom logic here
        pass

    @property
    def priority(self) -> int:
        return 85  # Higher = evaluated first

# Register the evaluator
service = JSLTService()
service.register_evaluator(CustomEvaluator(service))
```

### Core Functionality
- **Path expressions**: `.field`, `.array[0]`, `.nested.field`
- **Object construction**: `{ "key": .value }`
- **Array construction**: `[.item1, .item2]`
- **Variable system**: `let variable = expression` and `$variable` references
- **Control flow**: `for (.array) expression`, `if (condition) then else`
- **Operators**: Comparisons (`>=`, `<`, `==`) and string/number concatenation (`+`)

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   python start.py
   ```

The API will be available at:
- **Server**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Development

### Running Tests
```bash
pytest
```

### Testing with Debug Scripts
The backend includes several debug/test scripts for development:
- `test_variables.py` - Test variable functionality
- `test_direct.py` - Direct JSLT service testing
- `debug_*.py` - Various debugging utilities

### Configuration
Application settings are managed in `app/core/config.py`:
- **CORS origins**: Configure allowed frontend URLs
- **API prefix**: Customize API endpoint prefix
- **Debug mode**: Enable/disable debug features

### Project Structure Details

- **`app/api/`**: REST API endpoints and request/response handling
- **`app/core/`**: Application configuration and settings
- **`app/models/`**: Pydantic models for request/response validation
- **`app/services/jslt/`**: Refactored JSLT interpreter with modular architecture
  - **`evaluators/`**: Expression evaluators using the Strategy pattern
  - **`functions/`**: Built-in and custom function implementations
  - **`utils/`**: Parsing and utility functions
  - **`jslt_service.py`**: Main service orchestrator
- **`start.py`**: Uvicorn server configuration and application startup

### Design Patterns Used

- **Strategy Pattern**: Each evaluator is a strategy for handling specific expression types
- **Chain of Responsibility**: Evaluators are tried in priority order until one matches
- **Template Method**: Base classes define the structure, subclasses provide implementation
- **Dependency Injection**: Service reference passed to evaluators for recursive evaluation

## Error Handling

The API provides comprehensive error handling:
- **Syntax errors**: Detailed parsing error messages
- **Runtime errors**: Clear execution error descriptions
- **Validation errors**: Input validation with helpful suggestions
- **Performance monitoring**: Execution time tracking

## Integration

This backend is designed to work with the React frontend in the `../frontend` directory. The CORS configuration allows requests from `http://localhost:3000` by default.

For production deployment, update the CORS origins in `app/core/config.py` to match your frontend URL.

TODO:
- add correct conditionals if, else
    if (.foo.bar)
        {
            "array" : [for (.foo.bar) string(.)],
            "size"  : size(.foo.bar)
        }
    else
        "No array today"