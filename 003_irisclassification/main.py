# to get iris dataset
from sklearn import datasets

# get random forest
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import streamlit as st

# Animated text
st.markdown(
    """
    <style>
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    .animated-text {
        animation: fadeIn 2s ease-in-out;
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    <h1 class="animated-text">Iris Classification App</h1>
    """,
    unsafe_allow_html=True,
)

st.write(
    """
This app predicts the 🌼**Iris Flower**🌼 type based on YOUR input!
# """
)

# this creates a sidebar
st.sidebar.header("User Input Parameters")


def user_input_features():
    # takes arguement(min, max, and wht value you want it to default within range)
    sepal_length = st.sidebar.slider("Sepal length", 4.3, 7.9, 5.6)

    # sepal width
    sepal_width = st.sidebar.slider("Sepal width", 2.0, 4.4, 3.4)

    # petal length
    petal_length = st.sidebar.slider("Petal length", 1.0, 6.9, 4.7)

    # petal width
    petal_width = st.sidebar.slider("Petal width", 0.1, 2.5, 0.9)

    # storing the parameters in a diictionary so can make dataframe
    data = {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width,
    }

    print(data)

    user_features = pd.DataFrame(data, index=[0])

    return user_features


# what user wants
df = user_input_features()

# showing the wht user chooses
st.subheader("User Input parameters")
st.write(df)

# load iris dataset
iris = datasets.load_iris()

# by default, this bundle dataset if x is .data and y is.target
X = iris.data
Y = iris.target


# print(X)

# initializing random forest classifier
clf = RandomForestClassifier()

# fitting data to model
clf.fit(X, Y)

# this will give wht the random forest predict based on user
prediction = clf.predict(df)

# returns the probability of the
prediction_proba = clf.predict_proba(df)

# subheader
st.subheader("Class labels and their corresponding index number")
target_df = pd.DataFrame(iris.target_names, columns=["species"])
# st.write(iris.target_names)
st.write(target_df)

# prediction
st.subheader("Prediction")
st.write(iris.target_names[prediction])

## prediction proba
# st.subheader("Prediction probability")
# st.write(prediction_proba)

proba_df = pd.DataFrame(prediction_proba, columns=["Setosa", "Versicolor", "Virginica"])
st.write(proba_df)
