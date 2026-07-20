from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

SCALER_PATH = Path("../preprocessing/encoders/minmax_scaler.pkl")


def normalize_features(df):
    SCALER_PATH.parent.mkdir(parents=True, exist_ok=True)

    numeric_columns = [
        "view_count",
        "comment_count",
        "search_count",
        "interaction_count_x",
        "interaction_count_y",
        "target_score",
        "account_age_days",
        "total_views",
        "total_likes",
        "total_saves",
        "total_shares",
        "total_comments",
        "total_searches",
        "avg_interaction_weight",
        "runtime",
        "release_year",
        "rate",
        "popularity",
        "preferred_runtime",
        "preferred_release_year",
    ]

    if SCALER_PATH.exists():
        scaler = joblib.load(SCALER_PATH)
    else:
        scaler = MinMaxScaler()
        scaler.fit(df[numeric_columns])
        joblib.dump(scaler, SCALER_PATH)

    df[numeric_columns] = scaler.transform(df[numeric_columns])

    return df
