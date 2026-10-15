# Food Delivery Order Analytics Pipeline

A real-time data engineering prototype that simulates food delivery orders, streams events through Apache Kafka, validates and processes them using Python, stores them in Supabase PostgreSQL, and visualizes analytics through Streamlit.

## Architecture

```text
Python Order Producer
        |
        v
Apache Kafka (food-orders topic)
        |
        v
Kafka Consumer
        |
        v
Data Validation and Processing
        |
        v
Supabase PostgreSQL
        |
        v
Streamlit Analytics Dashboard
```

## Tech Stack

- **Python** — Order generation and processing
- **uv** — Python project and dependency management
- **Apache Kafka** — Real-time event streaming and queuing
- **Docker** — Runs Kafka locally
- **Supabase PostgreSQL** — Persistent order storage
- **SQLAlchemy** — Database connectivity
- **Streamlit** — Analytics dashboard
- **Plotly** — Data visualization
- **pytest** — Testing data validation

## Prerequisites

Install the following on macOS or Windows:

1. Git
2. Python 3.11 or later
3. uv
4. Docker Desktop
5. A Supabase account and PostgreSQL project

Verify your installations:

```bash
git --version
python --version
uv --version
docker --version
docker compose version
```

On Windows, `python --version` can also be replaced with `py --version`.

### Install uv

**macOS — Terminal**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal if required.

**Windows — PowerShell**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart PowerShell if required.

Install Docker Desktop from:

https://www.docker.com/products/docker-desktop/

Start Docker Desktop before running the pipeline.

## 1. Get the project

If the project is hosted on GitHub:

```bash
git clone <YOUR_REPOSITORY_URL>
cd food-delivery-analytics
```

Replace the placeholder with your repository URL.

Alternatively, copy the project folder to the new computer and open it in VS Code.

## 2. Install dependencies

Run from the project root:

```bash
uv sync
```

This creates or updates the virtual environment and installs the dependencies declared in `pyproject.toml` and its lockfile, if present.

Ensure the following dependencies are included:

- kafka-python-ng
- sqlalchemy
- psycopg[binary]
- pandas
- streamlit
- plotly
- python-dotenv
- faker
- pytest

If dependencies are missing from `pyproject.toml`, add them with:

```bash
uv add kafka-python-ng sqlalchemy "psycopg[binary]" pandas streamlit plotly python-dotenv faker
uv add --dev pytest
```

## 3. Configure Supabase PostgreSQL

1. Open https://supabase.com/dashboard.
2. Select your project.
3. Open the Connect panel.
4. Copy the PostgreSQL connection details.
5. Prefer the Session Pooler when a direct connection is unavailable on your network.

Create a `.env` file in the project root.

```env
DATABASE_URL=postgresql+psycopg://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/YOUR_DATABASE
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

Replace the database placeholders with the actual values supplied by Supabase. If using a pooler, use its provided username, host, port, and database name.

URL-encode special characters in the password if necessary.

**Security:** Never commit `.env` or expose database credentials publicly. Add `.env` to `.gitignore`.

## 4. Test the database connection

Run from the project root:

```bash
uv run --env-file .env python -c "from sqlalchemy import create_engine, text; import os; e=create_engine(os.environ['DATABASE_URL']); print(e.connect().execute(text('SELECT 1')).scalar()); e.dispose()"
```

Expected output:

```text
1
```

If the connection fails, verify the credentials, hostname, port, network access, and SSL requirements in your Supabase connection settings.

## 5. Start Kafka

Start Docker Desktop first, then run:

```bash
docker compose up -d kafka
```

Check the container:

```bash
docker compose ps
```

Kafka should be running and expose port `9092`.

Create the topic:

```bash
docker exec food-delivery-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic food-orders --partitions 3 --replication-factor 1
```

If Kafka reports that the topic already exists, continue.

Verify the topic:

```bash
docker exec food-delivery-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

Expected topic:

```text
food-orders
```

## 6. Run the pipeline

Keep three terminals open in VS Code. Run every command from the project root.

### Terminal 1: Start the Kafka consumer

```bash
uv run --env-file .env python -m food_delivery_analytics.consumer
```

The consumer reads events from Kafka, validates them, and stores processed events in Supabase PostgreSQL.

### Terminal 2: Start the order producer

```bash
uv run --env-file .env python -m food_delivery_analytics.producer
```

The producer generates simulated food delivery orders continuously and publishes them to Kafka.

You should see order IDs, restaurant names, amounts, partitions, and offsets.

### Terminal 3: Start the dashboard

```bash
uv run --env-file .env streamlit run dashboard/app.py
```

Open the URL printed in the terminal, usually:

http://localhost:8501

The dashboard displays order counts, revenue, average order value, cancellation rate, restaurant performance, and hourly order trends.

## 7. Verify that everything works

1. Confirm that Kafka is running.
2. Confirm that the producer publishes new order events.
3. Confirm that the consumer receives and stores events.
4. Open Supabase Dashboard → Table Editor → `orders`.
5. Verify that new order rows appear.
6. Open Streamlit and check that analytics update as new orders arrive.

## 8. Stop the pipeline

Press `Ctrl+C` in each terminal running the producer, consumer, and dashboard.

Stop Kafka:

```bash
docker compose stop kafka
```

Restart it later with:

```bash
docker compose start kafka
```

Kafka data is persisted in a Docker volume. Supabase data remains stored remotely.

## 9. Troubleshooting

### Kafka connection refused

Ensure Docker Desktop is running and check:

```bash
docker compose ps
docker logs food-delivery-kafka
```

### Kafka topic does not exist

Run the topic creation command in Step 5.

### Supabase authentication or connection failure

Check `.env`, the database password, connection string, pooler configuration, and network access.

### ModuleNotFoundError

Run:

```bash
uv sync
```

Ensure `src/food_delivery_analytics/__init__.py` exists and the project is configured correctly in `pyproject.toml`.

### Dashboard cannot find the orders table

Start the consumer and confirm it initializes the database table. Check the consumer logs and Supabase Table Editor.

### Port already in use

Check whether another process is using port `9092` or `8501`, and stop that process or change the corresponding port configuration.

## Important Notes

- This is a local development prototype, not a production deployment.
- Kafka is single-node and configured for development.
- Supabase is the persistent database; a local PostgreSQL container is not required.
- The consumer currently uses basic retry and invalid-message handling. A production version should include a dead-letter queue, robust offset management, and stronger idempotency.
- Revenue calculations should be updated before supporting multiple status-update events per order.

## Data Flow Summary

**Generate → Queue → Consume → Validate → Store → Analyze → Visualize**

This prototype demonstrates real-time event ingestion, message queuing, data quality validation, persistent storage, SQL analytics, and dashboard visualization.
