from sqlalchemy import text
from sqlalchemy.engine import Engine


def get_overview(engine: Engine) -> dict:
    """Return overall order and revenue metrics."""

    query = text("""
        SELECT
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT order_id) FILTER (
                WHERE status = 'CANCELLED'
            ) AS cancelled_orders,
            COALESCE(SUM(amount) FILTER (
                WHERE status != 'CANCELLED'
            ), 0) AS revenue,
            COALESCE(AVG(amount) FILTER (
                WHERE status != 'CANCELLED'
            ), 0) AS average_order_value
        FROM orders
    """)

    with engine.connect() as connection:
        row = connection.execute(query).mappings().one()
        return dict(row)


def get_restaurant_performance(engine: Engine) -> list[dict]:
    """Return order and revenue metrics grouped by restaurant."""

    query = text("""
        SELECT
            restaurant,
            COUNT(DISTINCT order_id) AS total_orders,
            COALESCE(SUM(amount) FILTER (
                WHERE status != 'CANCELLED'
            ), 0) AS revenue,
            COUNT(DISTINCT order_id) FILTER (
                WHERE status = 'CANCELLED'
            ) AS cancelled_orders
        FROM orders
        GROUP BY restaurant
        ORDER BY revenue DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
        return [dict(row) for row in result]


def get_hourly_orders(engine: Engine) -> list[dict]:
    """Return order counts grouped by hour."""

    query = text("""
        SELECT
            date_trunc('hour', created_at) AS hour,
            COUNT(DISTINCT order_id) AS total_orders
        FROM orders
        GROUP BY date_trunc('hour', created_at)
        ORDER BY hour
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
        return [dict(row) for row in result]
