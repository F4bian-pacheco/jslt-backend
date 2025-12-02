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

### API Features
- **RESTful API**: Transform and validation endpoints with FastAPI
- **Real-time Processing**: Fast JSON transformation and validation
- **CORS Support**: Configured for frontend integration
- **Error Handling**: Comprehensive error messages and suggestions
- **Performance Monitoring**: Execution time tracking
- **OpenAPI Documentation**: Auto-generated interactive docs at `/docs`

### JSLT Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| **Core Features** | | |
| Dot accessors (`.field`) | ✅ | Fully supported |
| Array indexing (`[0]`) | ✅ | Positive indices only |
| Array slicing (`[1:3]`) | ❌ | Not implemented |
| Negative indexing (`[-1]`) | ❌ | Not implemented |
| Object construction | ✅ | Full support |
| Array construction | ✅ | Full support |
| **Variables** | | |
| `let` statements | ✅ | With proper scoping |
| Variable references (`$var` or `var`) | ✅ | Both syntaxes supported |
| **Control Flow** | | |
| `if-else` conditionals | ✅ | With optional else |
| `for` array loops | ✅ | With filtering support |
| Object `for` loops | ❌ | Not implemented |
| **Operators** | | |
| Arithmetic (`+`, `-`, `*`, `/`, `%`) | ✅ | Full support with precedence |
| Comparison (`>`, `>=`, `<`, `<=`, `==`, `!=`) | ✅ | Full support |
| Boolean (`and`, `or`, `not()`) | ✅ | Full support |
| Pipe operator (`\|`) | ❌ | Not implemented |
| **Functions** | | |
| `size()` | ✅ | Arrays, objects, strings |
| `string()` | ✅ | Type conversion |
| `number()` | ✅ | Type conversion |
| `boolean()` | ✅ | Type conversion |
| `round()` | ✅ | Math function |
| Other built-in functions | ❌ | ~50+ functions missing |
| **Advanced** | | |
| Function declarations (`def`) | ❌ | Not implemented |
| Import statements | ❌ | Not implemented |
| Object matching (`* : .`) | ❌ | Not implemented |
| Dynamic keys | ❌ | Not implemented |
| Comments | ❌ | Not implemented |

**Implementation Coverage:** ~45% of JSLT specification

### Architecture
- **Clean Architecture**: Clear separation of concerns
- **Strategy Pattern**: Each evaluator handles specific expression types
- **Chain of Responsibility**: Evaluators tried in priority order
- **Extensible Design**: Easy to add custom functions and evaluators

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

The project uses pytest for testing. All tests are located in the `tests/` directory.

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
pytest tests/test_conditionals.py
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html
```

**Test Suite:**
- `tests/test_conditionals.py` - Conditional expressions (if-else) tests (6 tests)
- `tests/test_jslt_examples.py` - Official JSLT documentation examples (5 tests)
- `tests/test_api_conditional.py` - API integration tests (requires server running)

**Current Status:** ✅ 11 passed, 1 skipped

For more details, see [tests/README.md](tests/README.md)

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

## JSLT Tutorial & Language Features

This backend implements a subset of the official JSLT specification. Below is a tutorial of the supported features.

### Basic Concepts

JSLT expressions are evaluated against an input JSON document (the "context node"). The result is always JSON.

**Input:**
```json
{"foo": {"bar": [1, 2, 3, 4, 5]}}
```

### ✅ Implemented Features

#### 1. **Dot Accessors** - Access object properties
```jslt
.foo              // Returns: {"bar": [1, 2, 3, 4, 5]}
.foo.bar          // Returns: [1, 2, 3, 4, 5]
.                 // Returns the entire context node
```

#### 2. **Array Indexing** - Access array elements
```jslt
.foo.bar[0]       // Returns: 1
.foo.bar[-1]      // Returns: 5 (last element)
```

#### 3. **JSON Construction** - Build new objects and arrays
```jslt
{
  "array": .foo.bar,
  "size": size(.foo.bar)
}
// Returns: {"array": [1,2,3,4,5], "size": 5}
```

#### 4. **Variables** - Store and reuse values
```jslt
let count = size(.foo.bar)
{
  "total": $count,
  "doubled": $count * 2
}
```

**Scope rules:**
- Variables defined at top level are global
- Variables inside `for`, `if`, or objects are local to that scope

#### 5. **Conditionals (if-else)** - Conditional logic
```jslt
if (<condition>) <then-expr> else <else-expr>
```

The `else` clause is optional. If omitted, returns `null` when condition is false.

**Example:**
```jslt
if (.foo.bar)
    {
        "array": [for (.foo.bar) string(.)],
        "size": size(.foo.bar)
    }
else
    "No array today"
```

**Falsy values:** `false`, `null`, `{}`, `[]`  
**Truthy values:** Everything else (including `0`, `""`)

**Explicit null check:**
```jslt
if (.foo.bar != null)
    // Distinguishes between null and empty array
else
    "missing"
```

#### 6. **For Expressions** - Transform arrays
```jslt
[for (.foo.bar) string(.)]
// Returns: ["1", "2", "3", "4", "5"]
```

**With variables:**
```jslt
[for (.foo.bar)
  let doubled = . * 2
  $doubled
]
```

**With filtering:**
```jslt
[for (.foo.bar) . if (. > 3)]
// Returns: [4, 5]
```

#### 7. **Built-in Functions**
- `size(value)` - Length of array, object, or string
- `string(value)` - Convert to string
- `number(value)` - Convert to number
- `boolean(value)` - Convert to boolean
- `round(number)` - Round to nearest integer

**Example:**
```jslt
{
  "count": size(.items),
  "first": string(.items[0]),
  "isValid": boolean(.status)
}
```

#### 8. **Operators**
**Arithmetic:** `+`, `-`, `*`, `/`, `%` (with proper precedence)
```jslt
.price * .quantity - .discount  // Multiplication first, then subtraction = (100 * 2) - 10 = 190
.total / .count                  // Division
.number % 5                      // Modulo
```

**Comparison:** `>`, `>=`, `<`, `<=`, `==`, `!=`
```jslt
.age >= 18
.status == "active"
```

**String concatenation:**
```jslt
"Hello " + .name
```

**Boolean:** `and`, `or`, `not()`
```jslt
.age >= 18 and .hasLicense
```

#### 9. **Object Construction**
```jslt
{
  "name": .user.name,
  "adult": .user.age >= 18,
  "skillCount": size(.user.skills)
}
```

#### 10. **Array Construction**
```jslt
[.item1, .item2, .item3]
```

### 🚀 Quick Examples

**Example 1: Simple transformation**
```jslt
{
  "fullName": .firstName + " " + .lastName,
  "isAdult": .age >= 18
}
```

**Example 2: Array processing**
```jslt
let items = .cart.items
{
  "total": size($items),
  "names": [for ($items) .name],
  "expensive": [for ($items) . if (.price > 100)]
}
```

**Example 3: Conditional with nested data**
```jslt
if (.user)
  {
    "username": .user.name,
    "roles": [for (.user.roles) string(.)],
    "isAdmin": .user.role == "admin"
  }
else
  {"error": "No user found"}
```

### ❌ Not Yet Implemented

The following JSLT features are **not currently supported**:

#### Core Features
- [ ] **Array slicing** - `[1:3]`, `[:-1]` syntax
- [ ] **Negative array indexing** - `.array[-1]`
- [ ] **Object for expressions** - `{for (.) .key : .value}`
- [ ] **Object matching (spread)** - `{* : .}`, `{* - excluded : .}`
- [ ] **Dynamic keys** - `{.keyName : .value}`
- [ ] **Pipe operator** - `.a | [.b, .c]`

#### Advanced Features
- [ ] **Function declarations** - `def myFunc(param) ...`
- [ ] **Import statements** - `import "module.jslt" as mod`
- [ ] **Recursive functions**
- [ ] **Custom user functions** (only built-in functions supported)

#### Additional Operators & Functions
- [ ] **String slicing** - `.name[:5]`
- [ ] **More built-in functions** - `contains()`, `starts-with()`, `ends-with()`, `split()`, `join()`, etc.
- [ ] **Math functions** - `floor()`, `ceil()`, `abs()`, `min()`, `max()`
- [ ] **Type checking functions** - `is-string()`, `is-number()`, `is-array()`, `is-object()`
- [ ] **Array functions** - `flatten()`, `reverse()`, `sum()`, `all()`, `any()`
- [ ] **Date/time functions** - `parse-time()`, `format-time()`

#### Other
- [ ] **Comments** - `// comment` syntax
- [ ] **Multiline strings**
- [ ] **Null coalescing** - Special null handling
- [ ] **Error messages with suggestions** (basic error handling only)

### 📚 References

- [Official JSLT Repository](https://github.com/schibsted/jslt)
- [JSLT Tutorial](https://github.com/schibsted/jslt/blob/master/tutorial.md)
- [JSLT Function Documentation](https://github.com/schibsted/jslt/blob/master/functions.md)
- [JSLT Quick Reference](https://github.com/schibsted/jslt#quick-reference)

### 🎯 Roadmap

Priority features for future implementation:

1. **High Priority:**
   - Array slicing `[1:3]`
   - More built-in functions (`contains`, `split`, `join`)
   - Object matching/spread syntax `{* : .}`
   - Type checking functions

2. **Medium Priority:**
   - Object for expressions `{for (.) .key : .value}`
   - Pipe operator `.a | [.b, .c]`
   - String slicing
   - Math functions

3. **Low Priority:**
   - Function declarations `def`
   - Import statements
   - Comments support
   - Advanced error suggestions