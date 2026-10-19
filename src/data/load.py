"""Carrega Iris como DataFrame."""
import pandas as pd
from sklearn.datasets import load_iris

def load_iris_df():
    iris = load_iris(as_frame=True)
    df = iris.frame
    df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "target"]
    return df

if __name__ == "__main__":
    df = load_iris_df()
    print(df.head())
    print(f"\nShape: {df.shape}")