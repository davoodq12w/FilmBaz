from pathlib import Path
import joblib
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def days_since_last_interaction(df):
    reference_time = df["last_interaction"].max()
    df["days_since_last_interaction"] = (reference_time - df["last_interaction"]).dt.total_seconds() / 86400
    df.drop(columns=["last_interaction"], inplace=True)

    return df

