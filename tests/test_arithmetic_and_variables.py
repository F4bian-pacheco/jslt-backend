"""Tests for arithmetic operators and variable references."""

import pytest
from app.services.jslt.jslt_service import JSLTService


@pytest.fixture
def service():
    """Create a JSLTService instance."""
    return JSLTService()


def test_multiplication(service):
    """Test multiplication operator."""
    data = {"price": 100, "quantity": 2}
    result = service._evaluate_expression(".price * .quantity", data, {})
    assert result == 200


def test_division(service):
    """Test division operator."""
    data = {"total": 100, "count": 4}
    result = service._evaluate_expression(".total / .count", data, {})
    assert result == 25


def test_modulo(service):
    """Test modulo operator."""
    data = {"number": 17, "divisor": 5}
    result = service._evaluate_expression(".number % .divisor", data, {})
    assert result == 2


def test_subtraction(service):
    """Test subtraction operator."""
    data = {"max": 100, "min": 30}
    result = service._evaluate_expression(".max - .min", data, {})
    assert result == 70


def test_variable_reference_without_dollar(service):
    """Test variable reference without $ prefix."""
    data = {"orders": [1, 2, 3]}
    variables = {"orderCount": 3}
    result = service._evaluate_expression("orderCount", data, variables)
    assert result == 3


def test_complex_arithmetic_in_object(service):
    """Test complex arithmetic expressions in object construction."""
    data = {"price": 100, "quantity": 2, "discount": 10}
    result = service._evaluate_expression(
        '{ "subtotal": .price * .quantity, "total": .price * .quantity - .discount }',
        data,
        {},
    )
    assert result == {"subtotal": 200, "total": 190}


def test_for_loop_with_arithmetic(service):
    """Test for loop with arithmetic operations."""
    data = {
        "items": [
            {"price": 100, "qty": 2},
            {"price": 50, "qty": 3},
        ]
    }
    result = service._evaluate_expression(
        '[for (.items) { "total": .price * .qty }]', data, {}
    )
    assert result == [{"total": 200}, {"total": 150}]


def test_complete_user_expression(service):
    """Test complete user expression with multiple features."""
    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "status": "active",
        "orders": [
            {"product": "Laptop", "price": 1000, "quantity": 2},
            {"product": "Mouse", "price": 25, "quantity": 5},
        ],
    }

    expression = """
let orderCount = size(.orders)
let totalAmount = 2125

{
  "customerName": .name,
  "email": .email,
  "isAdult": if (.age >= 18) true else false,
  "accountStatus": if (.status == "active") "Active Account" else "Inactive Account",
  "orderSummary": {
    "totalOrders": orderCount,
    "totalAmount": totalAmount,
    "items": [for (.orders) {
      "name": .product,
      "subtotal": .price * .quantity
    }]
  }
}
"""

    result = service._evaluate_expression(expression.strip(), data, {})

    assert result["customerName"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["isAdult"] is True
    assert result["accountStatus"] == "Active Account"
    assert result["orderSummary"]["totalOrders"] == 2
    assert result["orderSummary"]["totalAmount"] == 2125
    assert len(result["orderSummary"]["items"]) == 2
    assert result["orderSummary"]["items"][0] == {"name": "Laptop", "subtotal": 2000}
    assert result["orderSummary"]["items"][1] == {"name": "Mouse", "subtotal": 125}
