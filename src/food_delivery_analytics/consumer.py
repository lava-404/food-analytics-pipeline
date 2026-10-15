import json
import os
import time

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy.exc import SQLAlchemyError

from food_delivery_analytics.database import (
    get_engine,
    initialize_database,
    save_order,
)
from food_delivery_analytics.processor import (
    InvalidOrderError,
    process_order,
)

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
)
KAFKA_TOPIC = "food-orders"
CONSUMER_GROUP = "food-analytics-consumers"


def main() -> None:
    engine = get_engine()
    initialize_database(engine)

    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
        group_id=CONSUMER_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    consumer.subscribe([KAFKA_TOPIC])
    print(f"Listening for orders on '{KAFKA_TOPIC}'...")

    try:
        while True:
            batches = consumer.poll(timeout_ms=1000, max_records=100)

            for _, messages in batches.items():
                for message in messages:
                    try:
                        processed_order = process_order(message.value)
                        inserted = save_order(engine, processed_order)

                        if inserted:
                            print(
                                f"Stored order {processed_order['order_id']} | "
                                f"{processed_order['restaurant']} | "
                                f"₹{processed_order['amount']}"
                            )
                        else:
                            print(
                                f"Duplicate event skipped: "
                                f"{processed_order['event_id']}"
                            )

                        # Commit only after the database operation succeeds.
                        consumer.commit()

                    except InvalidOrderError as exc:
                        print(f"Invalid order rejected: {exc}")
                        # Prototype policy: skip invalid events.
                        consumer.commit()

                    except (SQLAlchemyError, KafkaError) as exc:
                        print(f"Processing failed; stopping for retry: {exc}")
                        time.sleep(2)
                        return

                    except (json.JSONDecodeError, KeyError, TypeError) as exc:
                        print(f"Malformed event: {exc}")
                        # Prototype policy: skip malformed events.
                        consumer.commit()

    except KeyboardInterrupt:
        print("\nStopping consumer...")

    finally:
        consumer.close()
        engine.dispose()


if __name__ == "__main__":
    main()