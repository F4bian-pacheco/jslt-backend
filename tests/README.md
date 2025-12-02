# Tests - JSLT Backend

Este directorio contiene todos los tests automatizados para el backend de JSLT.

## Estructura de Tests

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Configuración de pytest (fixtures globales)
├── test_conditionals.py     # Tests de condicionales if-else
├── test_jslt_examples.py    # Tests basados en docs oficiales JSLT
└── test_api_conditional.py  # Tests de integración de API (requiere servidor)
```

## Ejecutar Tests

### Todos los tests
```bash
pytest
```

### Tests con salida detallada
```bash
pytest -v
```

### Tests específicos
```bash
# Ejecutar un archivo específico
pytest tests/test_conditionals.py

# Ejecutar un test específico
pytest tests/test_conditionals.py::test_if_else_with_both_clauses
```

### Tests con cobertura (si pytest-cov está instalado)
```bash
pytest --cov=app --cov-report=html
```

### Excluir tests específicos
```bash
# Excluir tests lentos
pytest -m "not slow"

# Excluir tests de integración
pytest -m "not integration"
```

## Descripción de los Tests

### test_conditionals.py
Tests exhaustivos de la funcionalidad de condicionales `if-else`:
- ✅ `test_if_else_with_both_clauses` - If-else completo con ambas cláusulas
- ✅ `test_if_without_else` - If sin cláusula else (retorna null)
- ✅ `test_falsy_values` - Valores falsy: false, null, {}, []
- ✅ `test_truthy_values` - Valores truthy: true, números, strings, objetos/arrays no vacíos
- ✅ `test_explicit_null_check` - Verificación explícita con != null
- ✅ `test_nested_if` - Expresiones if anidadas

**Total: 6 tests**

### test_jslt_examples.py
Tests basados en la documentación oficial de JSLT:
- ✅ `test_readme_example` - Ejemplo exacto del README oficial
- ✅ `test_empty_array_case` - Caso de array vacío (falsy)
- ✅ `test_explicit_null_check` - Distinción entre null y array vacío
- ✅ `test_missing_field` - Campo completamente faltante
- ✅ `test_if_without_else_variations` - Variaciones de if sin else

**Total: 5 tests**

### test_api_conditional.py
Test de integración con la API REST (requiere servidor activo):
- ⏭️ `test_api_conditional` - Skipped por defecto (requiere `python start.py`)

**Total: 1 test (skipped)**

## Fixtures Disponibles

### `service` (definido en cada archivo de test)
Crea una instancia de `JSLTService` para testing.

```python
@pytest.fixture
def service():
    """Create a JSLTService instance for testing."""
    return JSLTService()
```

Uso:
```python
def test_example(service):
    result = service.transform(input_data, expression)
    assert result.success
```

## Configuración (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--disable-warnings",
]
```

## Tests de Integración (API)

Para ejecutar los tests de API que requieren el servidor:

1. **Iniciar el servidor** (Terminal 1):
   ```bash
   python start.py
   ```

2. **Ejecutar tests de API** (Terminal 2):
   ```bash
   pytest tests/test_api_conditional.py -v
   ```

O remover el marcador `@pytest.mark.skip` en el archivo.

## Agregar Nuevos Tests

### 1. Crear archivo de test
```python
"""Test description."""

import pytest
from app.services.jslt.jslt_service import JSLTService


@pytest.fixture
def service():
    """Create a JSLTService instance for testing."""
    return JSLTService()


def test_nueva_funcionalidad(service):
    """Test nueva funcionalidad."""
    # Arrange
    input_data = {"key": "value"}
    expression = ".key"
    
    # Act
    response = service.transform(input_data, expression)
    
    # Assert
    assert response.success
    assert response.output == "value"
```

### 2. Ejecutar el nuevo test
```bash
pytest tests/test_nuevo.py -v
```

## Mejores Prácticas

1. **Usar fixtures** para configuración común
2. **Nombres descriptivos** para tests: `test_<funcionalidad>_<escenario>`
3. **Documentar tests** con docstrings
4. **Seguir AAA pattern**: Arrange, Act, Assert
5. **Un assert por concepto** (preferiblemente)
6. **Tests independientes** - no dependan del orden de ejecución

## Ejemplo de Test Completo

```python
def test_if_with_complex_condition(service):
    """Test if with complex boolean condition."""
    # Arrange
    input_data = {"age": 25, "country": "USA"}
    expression = 'if (.age >= 18 and .country == "USA") "eligible" else "not eligible"'
    
    # Act
    response = service.transform(input_data, expression)
    
    # Assert
    assert response.success, f"Transform failed: {response.error}"
    assert response.output == "eligible"
    assert response.execution_time_ms > 0
```

## Troubleshooting

### ImportError: No module named 'app'
**Solución**: Asegúrate de que existe `tests/conftest.py` con:
```python
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### Tests no se descubren
**Solución**: Verifica que:
- Los archivos empiecen con `test_`
- Las funciones empiecen con `test_`
- Existe `tests/__init__.py`

### Fixture no encontrado
**Solución**: Define el fixture en el mismo archivo o en `conftest.py`

## Resultado Actual

```
11 passed, 1 skipped in 0.31s
```

✅ Todos los tests pasando correctamente!
