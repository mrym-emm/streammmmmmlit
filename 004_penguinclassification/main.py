import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

st.write(
    """

# Pingu Prediction App 🐧

This app predicts the **Palmer Penguin** species!
         
Followed along DataProfessors tutorial: [Here](https://www.youtube.com/watch?v=Eai1jaZrRDs&list=PLtqF5YXg7GLmCvTswG32NqQypOuYkPRUE&index=4)

Data originally obtained from the [PalmerPenguins library](https://github.com/allisonhorst/palmerpenguins) in R by Allison Horst.
"""
)

# create sidebar
st.sidebar.header("Input Features Here!")

# text in sidebar
st.sidebar.markdown(
    """
[Example of CSV input file](https://raw.githubusercontent.com/dataprofessor/data/master/penguins_example.csv)
"""
)

# Collects user input features into dataframe

# this will add a fileuploader widget in the sidebar
uploaded_file = st.sidebar.file_uploader(
    "Please drop your csv file here ⬇️", type=["csv"]
)

# if the user uplaods their own csv file, then just load tht
if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)

# then user can just slide values. but make sure the values correspond exactly to how we build the classifier model
else:

    def user_input():

        # qualitative
        island = st.sidebar.selectbox("Island", ("Biscoe", "Dream", "Torgersen"))
        sex = st.sidebar.selectbox("Sex", ("male", "female"))

        # quantitative
        bill_length_mm = st.sidebar.slider("Bill length (mm)", 32.1, 59.6, 43.9)
        bill_depth_mm = st.sidebar.slider("Bill depth (mm)", 13.0, 21.5, 17.2)
        flipper_length_mm = st.sidebar.slider(
            "Flipper length (mm)", 172.0, 231.0, 201.0
        )
        body_mass_g = st.sidebar.slider("Body mass (g)", 2700.0, 6300.0, 4207.0)

        # now we'll create the dictionary based on the slider
        # order is according to the original penguins dataframe
        data = {
            "island": island,
            "bill_length_mm": bill_length_mm,
            "bill_depth_mm": bill_depth_mm,
            "flipper_length_mm": flipper_length_mm,
            "body_mass_g": body_mass_g,
            "sex": sex,
        }
        features = pd.DataFrame(data, index=[0])
        return features

    input_df = user_input()


# for encoding its easeir to conbine the user input with entire penguins dataset
penguins_raw = pd.read_csv("penguins_cleaned.csv")  # this includes the target(species)
penguins = penguins_raw.drop(columns=["species"])

df = pd.concat([input_df, penguins], axis=0)
# st.write(df)
# st.write(penguins_raw.head())

## now is the part where we encode err thing
encode = ["sex", "island"]

for col in encode:
    # get the one hot encoding of the sex and island column
    dummy = pd.get_dummies(df[col], prefix=col)
    # combines the encoded columns wise
    df = pd.concat([df, dummy], axis=1)
    del df[col]

# then selects the first row of the df, since the user input is above it
df = df[:1]

# st.write(df)

# displays the user input features
st.subheader("User Input Features")

if uploaded_file is not None:
    st.write(df)
else:
    st.write("Awaiting CSV file to be uploaded. Currently using below values")
    st.write(df)

# load classifier
load_clf = pickle.load(open("penguins_clf.pkl", "rb"))

# apply model to make prediction
prediction = load_clf.predict(df)
prediction_proba = load_clf.predict_proba(df)

df_prediction_proba = pd.DataFrame(
    prediction_proba, columns=["Adelie", "Chinstrap", "Gentoo"]
)

# st.subheader("Prediction:")
st.markdown(
    "<h2 style='text-decoration: underline;'>Prediction</h2>", unsafe_allow_html=True
)

penguins_species = np.array(["Adelie", "Chinstrap", "Gentoo"])
st.write(penguins_species[prediction])

st.markdown(
    "<h2 style='text-decoration: underline;'>Prediction Probability</h2>",
    unsafe_allow_html=True,
)

st.write(df_prediction_proba)
