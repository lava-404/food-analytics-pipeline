CREATE TABLE IF NOT EXISTS orders (
    event_id VARCHAR PRIMARY KEY,
    order_id VARCHAR NOT NULL,
    customer_id VARCHAR NOT NULL,
    restaurant VARCHAR NOT NULL,
    amount DOUBLE PRECISION NOT NULL CHECK (amount > 0),
    status VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    raw_event JSON NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_order_id
    ON orders (order_id);

CREATE INDEX IF NOT EXISTS idx_orders_created_at
    ON orders (created_at);

CREATE INDEX IF NOT EXISTS idx_orders_restaurant
    ON orders (restaurant);

CREATE INDEX IF NOT EXISTS idx_orders_status
    ON orders (status);