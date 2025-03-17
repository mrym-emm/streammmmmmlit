# import sqlite3
# import random
# from datetime import datetime, timedelta

# # Connect to the database (creates if it doesn't exist)
# conn = sqlite3.connect("nafas.db")
# cursor = conn.cursor()

# # Create table
# cursor.execute(
#     """
#     CREATE TABLE IF NOT EXISTS aqi_data (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         city TEXT,
#         date TEXT,
#         aqi INTEGER
#     )
# """
# )

# # Generate dummy data (10 entries)
# cities = ["Kuala Lumpur", "Penang", "Johor", "Selangor", "Sarawak"]
# start_date = datetime(2025, 3, 1)

# for _ in range(10):
#     city = random.choice(cities)
#     date = (start_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
#     aqi = random.randint(50, 200)  # Fake AQI values
#     cursor.execute(
#         "INSERT INTO aqi_data (city, date, aqi) VALUES (?, ?, ?)", (city, date, aqi)
#     )

# conn.commit()
# conn.close()
# print("Dummy database created successfully!")


# import sqlite3

# # Connect to the database
# conn = sqlite3.connect("nafas.db")
# cursor = conn.cursor()

# # Fetch all data from the table
# cursor.execute("SELECT * FROM aqi_data")
# rows = cursor.fetchall()

# # Print results
# print("AQI Data in Database:")
# for row in rows:
#     print(row)

# conn.close()


import streamlit as st
import sqlite3
import pandas as pd

# Streamlit Title
st.title("AQI Data Viewer")

# Connect to the SQLite database
conn = sqlite3.connect("nafas.db")

# Read data into a Pandas DataFrame
df = pd.read_sql("SELECT * FROM aqi_data", conn)

# Close connection
conn.close()

# Display DataFrame in Streamlit
st.dataframe(df)

# Add a filter by city
city_filter = st.selectbox("Filter by City:", ["All"] + list(df["city"].unique()))

if city_filter != "All":
    df = df[df["city"] == city_filter]
    st.write(f"Showing data for: **{city_filter}**")

st.dataframe(df)
