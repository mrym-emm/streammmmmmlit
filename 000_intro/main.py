import streamlit as st
import pandas as pd


st.title("Simple Data Dashboard")

# upload file
uploaded_file = st.file_uploader("Choose a CSV file", type ="csv")

# if there is a file uploaded
if uploaded_file is not None:
    st.write("File Uploaded...")
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")

    # displays the first 5 rows of the data
    st.write(df.head())

    # summary of data
    st.subheader("Data Summary")
    st.write(df.describe())

    st.subheader("Filter Data")

    # converts the columns to list
    column = df.columns.tolist()

    # streamlit widget
    selected_column = st.selectbox("Select column", column)

    unique_values = df[selected_column].unique()

    selected_value = st.selectbox("Select column", unique_values)

    # filter out what we filter
    filtered_df = df[df[selected_column] == selected_value]

    st.write(filtered_df)

    # to see correlation between x column n y column
    st.subheader("Plot Data")
    x_column = st.selectbox("Selct x-axis column", column)
    y_column = st.selectbox("Selct y-axis column", column)

    # if they click on generate plot button
    if st.button("Generate Plot"):
        st.line_chart(filtered_df.set_index(x_column)[y_column])
    else:
        st.write("Waiting on file upload")

# run `streamlit run main.py` in terminal

