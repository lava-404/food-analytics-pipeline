import json
import os
import time
import uuid
from datetime import datetime, timezone

from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError

fake = Faker()

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
)
KAFKA_TOPIC = "food-orders"

RESTAURANTS = [
    "Burger Hub",
    "Pizza Palace",
    "Spice Garden",
    "Sushi World",
    "Taco Town",
]

STATUSES = ["PLACED", "PLACED", "PLACED", "CANCELLED"]


def create_order() -> dict:
    """Generate one realistic food delivery order event."""
    return {
        "event_id": str(uuid.uuid4()),
        "order_id": str(uuid.uuid4()),
        "customer_id": str(uuid.uuid4()),
        "restaurant": fake.random_element(RESTAURANTS),
        "amount": round(fake.pyfloat(min_value=100, max_value=1500), 2),
        "status": fake.random_element(STATUSES),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8"),
        acks="all",
        retries=5,
    )

    print(f"Publishing live orders to Kafka topic: {KAFKA_TOPIC}")

    try:
        while True:
            order = create_order()

            try:
                future = producer.send(
                    KAFKA_TOPIC,
                    key=order["order_id"],
                    value=order,
                )
                metadata = future.get(timeout=10)

                print(
                    f"Published order {order['order_id']} | "
                    f"{order['restaurant']} | "
                    f"₹{order['amount']} | "
                    f"partition={metadata.partition} "
                    f"offset={metadata.offset}"
                )

            except KafkaError as exc:
                print(f"Failed to publish order: {exc}")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping order producer...")

    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()