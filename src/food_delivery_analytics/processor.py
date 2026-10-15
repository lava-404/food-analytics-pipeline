from datetime import datetime
from typing import Any


VALID_STATUSES = {"PLACED", "CANCELLED", "CONFIRMED", "PREPARING", "DELIVERED"}


class InvalidOrderError(ValueError):
    """Raised when an order event fails validation."""


def process_order(order: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a food delivery order event."""

    required_fields = {
        "event_id",
        "order_id",
        "customer_id",
        "restaurant",
        "amount",
        "status",
        "created_at",
    }

    missing_fields = required_fields - order.keys()
    if missing_fields:
        raise InvalidOrderError(
            f"Missing required fields: {sorted(missing_fields)}"
        )

    for field in ("event_id", "order_id", "customer_id", "restaurant"):
        if not isinstance(order[field], str) or not order[field].strip():
            raise InvalidOrderError(f"{field} must be a non-empty string")

    try:
        amount = float(order["amount"])
    except (TypeError, ValueError) as exc:
        raise InvalidOrderError("amount must be numeric") from exc

    if not 0 < amount <= 100_000:
        raise InvalidOrderError("amount must be between 0 and 100000")

    status = str(order["status"]).upper()
    if status not in VALID_STATUSES:
        raise InvalidOrderError(f"Invalid order status: {status}")

    try:
        timestamp = datetime.fromisoformat(
            str(order["created_at"]).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise InvalidOrderError("created_at must be a valid ISO timestamp") from exc

    if timestamp.tzinfo is None:
        raise InvalidOrderError("created_at must include a timezone")

    processed_order = order.copy()
    processed_order["amount"] = round(amount, 2)
    processed_order["status"] = status
    processed_order["restaurant"] = order["restaurant"].strip()
    processed_order["created_at"] = timestamp.isoformat()

    return processed_order
