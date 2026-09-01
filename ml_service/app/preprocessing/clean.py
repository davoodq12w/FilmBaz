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


    bool_columns = [
        "is_series",
        "adult"
    ]

    df[bool_columns] = df[bool_columns].astype(bool)

    int_columns = [
        "user_id",
        "movie_id",
        "account_age_days",
        "total_views",
        "total_likes",
        "total_saves",
        "total_shares",
        "total_comments",
        "total_searches",
        "total_watches",
        "total_completes",
        "preferred_runtime",
        "preferred_release_year",
        "user_interaction_count",
        "active_days",
        "release_year",
        "runtime",
        "director_id",
        "writer_id",
        "producer_id",
        "popularity",
    ]

    df[int_columns] = df[int_columns].astype("int32")

    float_columns = [
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
        df[col] = df[col].apply(
            lambda x: literal_eval(x) if isinstance(x, str) else x
        )

    return df
