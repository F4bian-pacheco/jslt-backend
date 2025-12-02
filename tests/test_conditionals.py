"""Test script for JSLT conditional expressions (if-else)."""

import pytest
from app.services.jslt.jslt_service import JSLTService


@pytest.fixture
def service():
    """Create a JSLTService instance for testing."""
    return JSLTService()


def test_if_else_with_both_clauses(service):
    """Test if-else with both then and else clauses."""

    # Test with truthy condition
    input_data = {"foo": {"bar": [1, 2, 3]}}
    expression = '''if (.foo.bar)
    {
        "array" : [for (.foo.bar) string(.)],
        "size"  : size(.foo.bar)
    }
else
    "No array today"'''

    response = service.transform(input_data, expression)
    print("Test 1 - Truthy condition (has array):")
    print(f"Input: {input_data}")
    print(f"Response: {response}")
    assert response.success and response.output == {"array": ["1", "2", "3"], "size": 3}
    print("✓ PASSED\n")

    # Test with falsy condition (empty array)
    input_data_empty = {"foo": {"bar": []}}
    response = service.transform(input_data_empty, expression)
    print("Test 2 - Falsy condition (empty array):")
    print(f"Input: {input_data_empty}")
    print(f"Response: {response}")
    assert response.success and response.output == "No array today"
    print("✓ PASSED\n")

    # Test with falsy condition (null)
    input_data_null = {"foo": {}}
    response = service.transform(input_data_null, expression)
    print("Test 3 - Falsy condition (null/missing):")
    print(f"Input: {input_data_null}")
    print(f"Response: {response}")
    assert response.success and response.output == "No array today"
    print("✓ PASSED\n")


def test_if_without_else(service):
    """Test if expression without else clause."""

    # Test with truthy condition
    input_data = {"age": 25}
    expression = 'if (.age >= 18) "adult"'

    response = service.transform(input_data, expression)
    print("Test 4 - If without else (truthy):")
    print(f"Input: {input_data}")
    print(f"Expression: {expression}")
    print(f"Response: {response}")
    assert response.success and response.output == "adult"
    print("✓ PASSED\n")

    # Test with falsy condition (should return null)
    input_data_young = {"age": 15}
    response = service.transform(input_data_young, expression)
    print("Test 5 - If without else (falsy, should return null):")
    print(f"Input: {input_data_young}")
    print(f"Expression: {expression}")
    print(f"Response: {response}")
    assert response.success and response.output is None
    print("✓ PASSED\n")


def test_falsy_values(service):
    """Test all JSLT falsy values."""

    test_cases = [
        ({"value": False}, ".value", "boolean false"),
        ({"value": None}, ".value", "null"),
        ({}, ".", "empty object"),
        ({"value": []}, ".value", "empty array"),
    ]

    expression = 'if (CONDITION) "truthy" else "falsy"'

    for input_data, condition, description in test_cases:
        expr = expression.replace("CONDITION", condition)
        response = service.transform(input_data, expr)
        print(f"Test Falsy - {description}:")
        print(f"Input: {input_data}")
        print(f"Condition: {condition}")
        print(f"Response: {response}")
        assert (
            response.success and response.output == "falsy"
        ), f"Expected 'falsy' but got {response.output}"
        print("✓ PASSED\n")


def test_truthy_values(service):
    """Test JSLT truthy values."""

    test_cases = [
        ({"value": True}, ".value", "boolean true"),
        ({"value": 1}, ".value", "number 1"),
        ({"value": 0}, ".value", "number 0"),
        ({"value": "text"}, ".value", "string"),
        ({"value": {"key": "val"}}, ".value", "non-empty object"),
        ({"value": [1]}, ".value", "non-empty array"),
    ]

    expression = 'if (CONDITION) "truthy" else "falsy"'

    for input_data, condition, description in test_cases:
        expr = expression.replace("CONDITION", condition)
        response = service.transform(input_data, expr)
        print(f"Test Truthy - {description}:")
        print(f"Input: {input_data}")
        print(f"Condition: {condition}")
        print(f"Response: {response}")
        assert (
            response.success and response.output == "truthy"
        ), f"Expected 'truthy' but got {response.output}"
        print("✓ PASSED\n")


def test_explicit_null_check(service):
    """Test explicit null check with != null."""

    # Test with value present
    input_data = {"foo": {"bar": []}}
    expression = 'if (.foo.bar != null) "has value" else "no value"'

    response = service.transform(input_data, expression)
    print("Test 6 - Explicit null check (value present, empty array):")
    print(f"Input: {input_data}")
    print(f"Response: {response}")
    assert response.success and response.output == "has value"
    print("✓ PASSED\n")

    # Test with null/missing value
    input_data_missing = {"foo": {}}
    response = service.transform(input_data_missing, expression)
    print("Test 7 - Explicit null check (value missing):")
    print(f"Input: {input_data_missing}")
    print(f"Response: {response}")
    assert response.success and response.output == "no value"
    print("✓ PASSED\n")


def test_nested_if(service):
    """Test nested if expressions."""

    input_data = {"age": 25, "hasLicense": True}
    expression = '''if (.age >= 18)
    if (.hasLicense)
        "can drive"
    else
        "too young to drive but has license"
else
    "too young"'''

    response = service.transform(input_data, expression)
    print("Test 8 - Nested if:")
    print(f"Input: {input_data}")
    print(f"Response: {response}")
    assert response.success and response.output == "can drive"
    print("✓ PASSED\n")
