from copy import deepcopy

import pytest

from food_delivery_analytics.processor import (
    InvalidOrderError,
    process_order,
)


@pytest.fixture
def valid_order():
    return {
        "event_id": "event-001",
        "order_id": "order-001",
        "customer_id": "customer-001",
        "restaurant": "Burger Hub",
        "amount": 299.50,
        "status": "PLACED",
        "created_at": "2026-10-15T12:00:00+00:00",
    }


def test_valid_order_is_processed(valid_order):
    result = process_order(valid_order)

    assert result["order_id"] == "order-001"
    assert result["amount"] == 299.50
    assert result["status"] == "PLACED"


def test_amount_is_normalized(valid_order):
    valid_order["amount"] = "450.5"

    result = process_order(valid_order)

    assert result["amount"] == 450.50


@pytest.mark.parametrize("amount", [0, -10, 100001, "invalid", None])
def test_invalid_amount_is_rejected(valid_order, amount):
    valid_order["amount"] = amount

   