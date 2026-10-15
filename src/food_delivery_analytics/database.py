import os
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.sql import func


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://food_admin:food_secret@localhost:5432/food_delivery",
)

metadata = MetaData()

orders = Table(
    "orders",
    metadata,
    Column("event_id", String, primary_key=True),
    Column("order_id", String, nullable=False),
    Column("customer_id", String, nullable=False),
    Column("restaurant", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("raw_event", JSON, nullable=False),
)


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL."""
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


def initialize_database(engine: Engine) -> None:
    """Create the orders table if it does not exist."""
    metadata.create_all(engine)


def save_order(engine: Engine, order: dict[str, Any]) -> bool:
    """Insert an order event; return False if it already exists."""

    from datetime import datetime

    created_at = datetime.fromisoformat(order["created_at"])

    statement = (
        insert(orders)
        .values(
            event_id=order["event_id"],
            order_id=order["order_id"],
            customer_id=order["customer_id"],
            restaurant=order["restaurant"],
            amount=order["amount"],
            status=order["status"],
            created_at=created_at,
            raw_event=order,
        )
        .on_conflict_do_nothing(index_elements=["event_id"])
        .returning(orders.c.event_id)
    )

    with engine.begin() as connection:
        result = connection.execute(statement)
        return result.scalar_one_or_none() is not None
