# so this module is created so we dont have to build the app over and over again
import pandas as pd

# loading penguins dataset from directory
penguins = pd.read_csv("penguins_cleaned.csv")

print(penguins.head())
print("Hello")

