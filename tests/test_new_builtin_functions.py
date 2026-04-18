"""Tests for newly added path features and built-in functions."""

import pytest
from app.services.jslt.jslt_service import JSLTService


@pytest.fixture
def service():
    """Create a JSLTService instance for testing."""
    return JSLTService()


def test_array_slicing_variants(service):
    """Array slicing should support positive and negative bounds."""
    data = {"arr": [10, 20, 30, 40, 50]}

    assert service._evaluate_expression(".arr[1:3]", data, {}) == [20, 30]
    assert service._evaluate_expression(".arr[:-1]", data, {}) == [10, 20, 30, 40]
    assert service._evaluate_expression(".arr[1:]", data, {}) == [20, 30, 40, 50]
    assert service._evaluate_expression(".arr[-3:-1]", data, {}) == [30, 40]


def test_negative_indexing_and_invalid_access(service):
    """Negative indexing should return from end and invalid access should return null."""
    data = {"arr": ["a", "b", "c"]}

    assert service._evaluate_expression(".arr[-1]", data, {}) == "c"
    assert service._evaluate_expression(".arr[-4]", data, {}) is None
    assert service._evaluate_expression(".arr[bad]", data, {}) is None


def test_string_functions_with_null_handling(service):
    """String built-ins should be null-safe."""
    data = {
        "text": "  HeLLo World  ",
        "csv": "a,b,c",
        "items": ["foo", "bar", "baz"],
        "null_value": None,
    }

    assert service._evaluate_expression("lowercase(.text)", data, {}) == "  hello world  "
    assert service._evaluate_expression("uppercase(.text)", data, {}) == "  HELLO WORLD  "
    assert service._evaluate_expression("trim(.text)", data, {}) == "HeLLo World"
    assert service._evaluate_expression("split(.csv, ',')", data, {}) == ["a", "b", "c"]
    assert service._evaluate_expression("join(.items, '-')", data, {}) == "foo-bar-baz"

    assert service._evaluate_expression("lowercase(.null_value)", data, {}) == ""
    assert service._evaluate_expression("uppercase(.null_value)", data, {}) == ""
    assert service._evaluate_expression("trim(.null_value)", data, {}) == ""
    assert service._evaluate_expression("split(.null_value, ',')", data, {}) == []
    assert service._evaluate_expression("join(.null_value, ',')", data, {}) == ""


def test_flatten_recursive(service):
    """Flatten should recursively flatten deeply nested arrays."""
    data = {"nested": [1, [2, [3, [4, [5]]]], [6, 7], 8]}
    assert service._evaluate_expression("flatten(.nested)", data, {}) == [1, 2, 3, 4, 5, 6, 7, 8]


def test_all_any_with_regular_and_empty_arrays(service):
    """all/any should follow standard truth table conventions, including empties."""
    data = {
        "all_true": [1, "x", True],
        "mixed": [1, 0, True],
        "empty": [],
    }

    assert service._evaluate_expression("all(.all_true)", data, {}) is True
    assert service._evaluate_expression("all(.mixed)", data, {}) is False
    assert service._evaluate_expression("any(.all_true)", data, {}) is True
    assert service._evaluate_expression("any(.mixed)", data, {}) is True
    assert service._evaluate_expression("all(.empty)", data, {}) is True
    assert service._evaluate_expression("any(.empty)", data, {}) is False


def test_floor_and_ceiling_with_positive_and_negative_values(service):
    """floor/ceiling should work for positive and negative decimals."""
    data = {"pos": 3.7, "neg": -3.2}

    assert service._evaluate_expression("floor(.pos)", data, {}) == 3
    assert service._evaluate_expression("ceiling(.pos)", data, {}) == 4
    assert service._evaluate_expression("floor(.neg)", data, {}) == -4
    assert service._evaluate_expression("ceiling(.neg)", data, {}) == -3


def test_min_max_multiple_arguments(service):
    """min/max should support variadic args and list arguments."""
    data = {"nums": [5, 2, 9, -1, 3]}

    assert service._evaluate_expression("min(5, 2, 9, -1, 3)", data, {}) == -1
    assert service._evaluate_expression("max(5, 2, 9, -1, 3)", data, {}) == 9
    assert service._evaluate_expression("min(.nums)", data, {}) == -1
    assert service._evaluate_expression("max(.nums)", data, {}) == 9


def test_min_raises_clear_error_for_non_numeric_argument(service):
    """min should raise a clear error when conversion to number fails."""
    data = {}

    with pytest.raises(ValueError, match=r"min\(\) expected numeric arguments"):
        service._evaluate_expression("min(1, 'x', 3)", data, {})


def test_max_raises_clear_error_for_non_numeric_list_item(service):
    """max should raise a clear error when list contains non-numeric values."""
    data = {"nums": [1, "x", 3]}

    with pytest.raises(ValueError, match=r"max\(\) expected numeric arguments"):
        service._evaluate_expression("max(.nums)", data, {})
