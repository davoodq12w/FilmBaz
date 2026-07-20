import pandas as pd
import numpy as np
from ast import literal_eval

def cleaned_data(df):

    df.replace(
        {
            "": np.nan,
            "None": np.nan,
            "null": np.nan,
            "[]": np.nan
        },
        inplace=True
    )

    df.dropna(
        subset=[
            "favorite_genres",
            "favorite_directors",
            "favorite_writers",
            "last_interaction",
            "preferred_runtime",
            "preferred_release_year",
        ],
        inplace=True
    )

    df.reset_index(drop=True, inplace=True)

    df[["director_id", "writer_id", "producer_id"]] = (
        df[["director_id", "writer_id", "producer_id"]]
        .fillna(0)
        .astype(int)
    )

    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)


    df["last_interaction"] = pd.to_datetime(
        df["last_interaction"],
        utc=True
    )


    bool_columns = [
        "liked",
        "saved",
        "shared",
        "is_series",
        "adult"
    ]

    df[bool_columns] = df[bool_columns].astype(bool)


    int_columns = [
        "user_id",
        "movie_id",
        "view_count",
        "comment_count",
        "search_count",
        "account_age_days",
        "total_views",
        "total_likes",
        "total_saves",
        "total_shares",
        "total_comments",
        "total_searches",
        "preferred_runtime",
        "preferred_release_year",
        "director_id",
        "writer_id",
        "producer_id",
        "release_year",
        "runtime",
        "popularity",
    ]

    df[int_columns] = df[int_columns].astype("int32")


    float_columns = [
        "interaction_count_x",
        "interaction_count_y",
        "target_score",
        "avg_interaction_weight",
        "rate",
    ]

    df[float_columns] = df[float_columns].astype("float32")


    list_columns = [
        "favorite_genres",
        "favorite_directors",
        "favorite_writers",
        "genres",
    ]

    for col in list_columns:
        df[col] = df[col].apply(literal_eval)

    return df
