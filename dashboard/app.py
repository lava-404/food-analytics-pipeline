import os
import time

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://food_admin:food_secret@localhost:5432/food_delivery",
)

st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="",
    layout="wide",
)

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def load_data():
    engine = get_engine()

    overview_query = text("""
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

    restaurant_query = text("""
        SELECT
            restaurant,
            COUNT(DISTINCT order_id) AS total_orders,
            COALESCE(SUM(amount) FILTER (
                WHERE status != 'CANCELLED'
            ), 0) AS revenue
        FROM orders
        GROUP BY restaurant
        ORDER BY revenue DESC
    """)

    hourly_query = text("""
        SELECT
            date_trunc('hour', created_at) AS hour,
            COUNT(DISTINCT order_id) AS total_orders
        FROM orders
        GROUP BY date_trunc('hour', created_at)
        ORDER BY hour
    """)

    with engine.connect() as connection:
        overview = pd.read_sql(overview_query, connection)
        restaurants = pd.read_sql(restaurant_query, connection)
        hourly = pd.read_sql(hourly_query, connection)

    return overview.iloc[0], restaurants, hourly


st.title("Food Delivery Order Analytics")
st.caption("Live order-stream monitoring dashboard")

auto_refresh = st.toggle("Auto-refresh every 5 seconds", value=True)

try:
    overview, restaurants, hourly = load_data()

    total_orders = int(overview["total_orders"])
    cancelled = int(overview["cancelled_orders"])
    revenue = float(overview["revenue"])
    average_order_value = float(overview["average_order_value"])

    cancellation_rate = (
        cancelled / total_orders * 100 if total_orders else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Revenue", f"₹{revenue:,.2f}")
    col3.metric("Avg. Order Value", f"₹{average_order_value:,.2f}")
    col4.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")

    st.subheader("Restaurant Performance")

    if not restaurants.empty:
        fig = px.bar(
            restaurants,
            x="restaurant",
            y="revenue",
            title="Revenue by Restaurant",
            labels={
                "restaurant": "Restaurant",
                "revenue": "Revenue (₹)",
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(restaurants, use_container_width=True)
    else:
        st.info("Waiting for orders to arrive.")

    st.subheader("Orders Over Time")

    if not hourly.empty:
        fig = px.line(
            hourly,
            x="hour",
            y="total_orders",
            markers=True,
            title="Orders per Hour",
            labels={
                "hour": "Hour",
                "total_orders": "Orders",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Last refreshed: {time.strftime('%H:%M:%S')}")

except Exception as exc:
    st.error(f"Unable to load analytics: {exc}")

if auto_refresh:
    time.sleep(5)
    st.rerun()
