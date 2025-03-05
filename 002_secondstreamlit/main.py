# Imports
import streamlit as st
import pandas as pd
import numpy as np
import csv
import random
import altair as alt

from altair import layer

#-----------------------------------------------------------------
# Intro
 # title block
st.title("Streamlit web app")

code = """def isnt_this_interesting:
print('It certainly is!')"""

st.code(code, language = "python")

#------------------------------------------------------------------
# Data

## random data from streamlit documentation
# chart_data = pd.DataFrame(np.random.randn(20, 3),
#                           columns=["a", "b", "c"])
#
# st.line_chart(chart_data)

with open("data.csv", 'r') as csv_files:
    reader = csv.reader(csv_files)
    next(reader, None)

    # initializing empty list to store name of each row
    names = []
    grades = []

    for line in reader:
        # print(line) # just to check if it works
        names.append(line[0])
        # print(names)

        grades.append([int(line[1]), int(line[2]), int(line[3]), int(line[4])])
        # print(grades)

    chart_data = pd.DataFrame(grades, index = names).T
    print(chart_data)

    st.line_chart(chart_data)

    # transpose to make sure subjects are indexed correctly
    chart_data = chart_data.T.reset_index()
    chart_data = chart_data.melt(id_vars=['index'], var_name='Subject', value_name='Score')

    # rename for clarity
    chart_data.rename(columns={'index': 'Student'}, inplace=True)

    # create grouped bar chart :N is nominal, :Q is quantitaive
    test = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Subject:N', title='Subjects', axis=alt.Axis(labelAngle=0)),  # Subjects on X-axis
        y=alt.Y('Score:Q', title='Scores'),  # Scores on Y-axis
        color=alt.Color('Student:N', legend=alt.Legend(title="Students")),  # Color by student
        xOffset=alt.X('Student:N')  # Offsets bars so they are grouped instead of stacked
    ).properties(width=500)

    # create the chart
    st.altair_chart(test, use_container_width=True)
