import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Streamlit Title
st.title("AQI Data Viewer")

# Database path
db_path = "nafas.db"


# Function to create and populate the database if it doesn't exist
def create_dummy_database():
    # Connect to the database (creates if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS aqi_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            date TEXT,
            aqi INTEGER
        )
        """
    )

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM aqi_data")
    count = cursor.fetchone()[0]

    # Generate dummy data only if table is empty
    if count == 0:
        cities = ["Kuala Lumpur", "Penang", "Johor", "Selangor", "Sarawak"]
        start_date = datetime(2025, 3, 1)

        for _ in range(10):
            city = random.choice(cities)
            date = (start_date + timedelta(days=random.randint(0, 30))).strftime(
                "%Y-%m-%d"
            )
            aqi = random.randint(50, 200)  # Fake AQI values
            cursor.execute(
                "INSERT INTO aqi_data (city, date, aqi) VALUES (?, ?, ?)",
                (city, date, aqi),
            )

        conn.commit()
        st.success("Dummy database created successfully!")

    conn.close()


# Check if the database exists, if not create it
db_exists = os.path.exists(db_path)
if not db_exists:
    st.warning("Database not found. Creating a new one with dummy data.")
    create_dummy_database()
else:
    # Check if the table exists and has data
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM aqi_data")
        count = cursor.fetchone()[0]
        conn.close()

        if count == 0:
            st.warning("Database exists but has no data. Adding dummy data.")
            create_dummy_database()
    except sqlite3.OperationalError:
        st.warning(
            "Database exists but table doesn't. Creating table and adding dummy data."
        )
        create_dummy_database()

try:
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Read data into a Pandas DataFrame
    df = pd.read_sql("SELECT * FROM aqi_data", conn)

    # Close connection
    conn.close()

    # Display DataFrame in Streamlit
    st.subheader("All AQI Data")
    st.dataframe(df)

    # Add a filter by city
    city_filter = st.selectbox("Filter by City:", ["All"] + list(df["city"].unique()))

    if city_filter != "All":
        filtered_df = df[df["city"] == city_filter]
        st.subheader(f"Filtered Data for {city_filter}")
        st.dataframe(filtered_df)

        # Add a simple visualization
        st.subheader(f"AQI Levels for {city_filter}")
        chart_df = filtered_df[["date", "aqi"]].set_index("date")
        st.line_chart(chart_df)
    else:
        # Show chart for all cities
        st.subheader("AQI Levels by City")
        pivot_df = df.pivot_table(
            index="date", columns="city", values="aqi", aggfunc="mean"
        )
        st.line_chart(pivot_df)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.exception(e)
