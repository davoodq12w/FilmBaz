from pathlib import Path
import joblib
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def create_last_interaction_feature(df):
    reference_time = df["last_interaction"].max()
    df["days_since_last_interaction"] = (reference_time - df["last_interaction"]).dt.total_seconds() / 86400
    df.drop(columns=["last_interaction"], inplace=True)

    return df


def encode_genres(df):
    ENCODER_PATH = Path("../preprocessing/encoders/genre_encoder.pkl")
    ENCODER_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_genres = pd.concat(
        [
            df["genres"],
            df["favorite_genres"],
        ],
        ignore_index=True,
    )
    current_genres = sorted(
        {
            genre
            for genres in all_genres
            for genre in genres
        }
    )

    rebuild_encoder = False

    if ENCODER_PATH.exists():
        genre_encoder = joblib.load(ENCODER_PATH)

        if set(current_genres) != set(genre_encoder.classes_):
            rebuild_encoder = True

    else:
        rebuild_encoder = True

    if rebuild_encoder:
        genre_encoder = MultiLabelBinarizer()
        genre_encoder.fit(all_genres)

        joblib.dump(
            genre_encoder,
            ENCODER_PATH,
        )

    genres_df = pd.DataFrame(
        genre_encoder.transform(df["genres"]),
        columns=[
            f"genre_{genre}"
            for genre in genre_encoder.classes_
        ],
        index=df.index,
    )
    favorite_genres_df = pd.DataFrame(
        genre_encoder.transform(df["favorite_genres"]),
        columns=[
            f"favorite_{genre}"
            for genre in genre_encoder.classes_
        ],
        index=df.index,
    )

    df = df.drop(
        columns=[
            "genres",
            "favorite_genres",
        ]
    )
    df = pd.concat(
        [
            df,
            genres_df,
            favorite_genres_df,
        ],
        axis=1,
    )

    return df


def encode_country(df):
    ENCODER_PATH = Path("../preprocessing/encoders/country_encoder.pkl")

    ENCODER_PATH.parent.mkdir(parents=True, exist_ok=True)

    current_countries = sorted(df["country"].dropna().unique())

    rebuild_encoder = False

    if ENCODER_PATH.exists():
        country_encoder = joblib.load(ENCODER_PATH)

        saved_countries = set(country_encoder.keys())

        if set(current_countries) != saved_countries:
            rebuild_encoder = True

    else:
        rebuild_encoder = True

    if rebuild_encoder:
        country_encoder = {
            country: idx
            for idx, country in enumerate(current_countries)
        }

        joblib.dump(country_encoder, ENCODER_PATH)

    df["country"] = df["country"].map(country_encoder).astype(int)

    return df
