"""Test examples from JSLT official documentation."""

import pytest
from app.services.jslt.jslt_service import JSLTService


@pytest.fixture
def service():
    """Create a JSLTService instance for testing."""
    return JSLTService()


def test_readme_example(service):
    """Test the exact example from the official JSLT README."""

    input_data = {"foo": {"bar": [1, 2, 3, 4, 5]}}

    expression = '''if (.foo.bar)
    {
        "array" : [for (.foo.bar) string(.)],
        "size"  : size(.foo.bar)
    }
else
    "No array today"'''

    response = service.transform(input_data, expression)

    print("README Example Test:")
    print(f"Input: {input_data}")
    print(f"Response: {response}")

    expected = {"array": ["1", "2", "3", "4", "5"], "size": 5}

    assert response.success, f"Transform failed: {response.error}"
    assert response.output == expected, f"Expected {expected}, got {response.output}"
    print("✓ PASSED\n")


def test_empty_array_case(service):
    """Test with empty array (falsy)."""

    input_data = {"foo": {"bar": []}}

    expression = '''if (.foo.bar)
    {
        "array" : [for (.foo.bar) string(.)],
        "size"  : size(.foo.bar)
    }
else
    "No array today"'''

    response = service.transform(input_data, expression)

    print("Empty Array Case:")
    print(f"Input: {input_data}")
    print(f"Response: {response}")

    assert response.success, f"Transform failed: {response.error}"
    assert (
        response.output == "No array today"
    ), f"Expected 'No array today', got {response.output}"
    print("✓ PASSED\n")


def test_explicit_null_check(service):
    """Test explicit null check as per JSLT documentation."""

    # Test with empty array (should pass != null check)
    input_data = {"foo": {"bar": []}}

    expression = '''if (.foo.bar != null)
    {
        "array" : [for (.foo.bar) string(.)],
        "size"  : size(.foo.bar)
    }
else
    "No array today"'''

    response = service.transform(input_data, expression)

    print("Explicit Null Check (empty array should pass):")
    print(f"Input: {input_data}")
    print(f"Response: {response}")

    expected = {"array": [], "size": 0}

    assert response.success, f"Transform failed: {response.error}"
    assert response.output == expected, f"Expected {expected}, got {response.output}"
    print("✓ PASSED\n")


def test_missing_field(service):
    """Test with completely missing field."""

    input_data = {"foo": {}}

    expression = '''if (.foo.bar != null)
    {
        "array" : [for (.foo.bar) string(.)],
        "size"  : size(.foo.bar)
    }
else
    "No array today"'''

    response = service.transform(input_data, expression)

    print("Missing Field Check:")
    print(f"Input: {input_data}")
    print(f"Response: {response}")

    assert response.success, f"Transform failed: {response.error}"
    assert (
        response.output == "No array today"
    ), f"Expected 'No array today', got {response.output}"
    print("✓ PASSED\n")


def test_if_without_else_variations(service):
    """Test if without else in different scenarios."""

    # Test 1: Condition is true
    response = service.transform({"value": "exists"}, 'if (.value) "found"')
    print("If without else (truthy):")
    print(f"Response: {response}")
    assert response.success and response.output == "found"
    print("✓ PASSED\n")

    # Test 2: Condition is false (should return null)
    response = service.transform({}, 'if (.value) "found"')
    print("If without else (falsy, returns null):")
    print(f"Response: {response}")
    assert response.success and response.output is None
    print("✓ PASSED\n")

    # Test 3: Complex expression in then clause
    response = service.transform(
        {"items": [1, 2, 3]},
        'if (.items) { "count": size(.items), "first": .items[0] }',
    )
    print("If without else (complex then clause):")
    print(f"Response: {response}")
    expected = {"count": 3, "first": 1}
    assert response.success and response.output == expected
    print("✓ PASSED\n")
