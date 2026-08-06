import tensorflow as tf
from sklearn.model_selection import train_test_split
from utils import get_latest_processed_dataset
import pandas as pd
from ast import literal_eval
from tensorflow.keras import layers, Model

df = pd.read_csv(get_latest_processed_dataset())
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

fetures = df.drop(["target_score"], axis=1)
target = df["target_score"]
X_train, X_test, y_train, y_test = train_test_split(fetures, target, test_size=0.2, random_state=42)

NUMERIC_COLUMNS = [
    "account_age_days",
    "total_views",
    "total_likes",
    "total_saves",
    "total_shares",
    "total_comments",
    "total_searches",
    "total_watches",
    "total_completes",
    "avg_interaction_weight",
    "preferred_runtime",
    "preferred_release_year",
    "user_interaction_count",
    "active_days",
    "rate",
    "release_year",
    "runtime",
    "popularity",
]

EMBEDDING_COLUMNS = [
    "user_id",
    "movie_id",
    "director_id",
    "writer_id",
    "producer_id",
    "country",
]

MULTI_EMBEDDING_COLUMNS = [
    "favorite_directors",
    "favorite_writers",
    "genres",
    "favorite_genres",
]

vocab_sizes = {
    "user_id": df["user_id"].nunique() + 1,
    "movie_id": df["movie_id"].nunique() + 1,
    "director_id": df["director_id"].nunique() + 1,
    "writer_id": df["writer_id"].nunique() + 1,
    "producer_id": df["producer_id"].nunique() + 1,
    "country": df["country"].nunique() + 1,
    "genres": df["genres"].explode().nunique() + 1,
    "favorite_directors": df["favorite_directors"].explode().nunique() + 1,
    "favorite_writers": df["favorite_writers"].explode().nunique() + 1,
}


def build_model():
    # ---------- Inputs ----------

    numeric_input = layers.Input(
        shape=(len(NUMERIC_COLUMNS),),
        name="numeric_features"
    )

    country_input = layers.Input(
        shape=(1,),
        dtype=tf.string,
        name="country"
    )

    director_input = layers.Input(shape=(1,), dtype=tf.int32, name="director_id")
    writer_input = layers.Input(shape=(1,), dtype=tf.int32, name="writer_id")
    producer_input = layers.Input(shape=(1,), dtype=tf.int32, name="producer_id")
    user_input = layers.Input(shape=(1,), dtype=tf.int32, name="user_id")
    movie_input = layers.Input(shape=(1,), dtype=tf.int32, name="movie_id")

    favorite_directors_input = layers.Input(
        shape=(None,),
        dtype=tf.int32,
        name="favorite_directors"
    )

    favorite_writers_input = layers.Input(
        shape=(None,),
        dtype=tf.int32,
        name="favorite_writers"
    )

    genres_input = layers.Input(
        shape=(None,),
        dtype=tf.int32,
        name="genres"
    )

    favorite_genres_input = layers.Input(
        shape=(None,),
        dtype=tf.int32,
        name="favorite_genres"
    )

    bool_input = layers.Input(
        shape=(2,),
        dtype=tf.float32,
        name="bool_features"
    )

    # ---------- Numeric ----------

    normalizer = layers.Normalization()
    numeric = normalizer(numeric_input)
    normalizer.adapt(
        X_train[NUMERIC_COLUMNS].values.astype("float32")
    )

    # ---------- Single Embeddings ----------
    country_lookup = layers.StringLookup(
        vocabulary=df["country"].unique(),
        mask_token=None
    )

    country = country_lookup(country_input)

    country = layers.Embedding(
        input_dim=country_lookup.vocabulary_size(),
        output_dim=16
    )(country)

    country = layers.Flatten()(country)

    director_lookup = layers.IntegerLookup(
        vocabulary=df["director_id"].unique(),
        mask_token=None
    )

    director = director_lookup(director_input)

    director = layers.Embedding(
        input_dim=director_lookup.vocabulary_size(),
        output_dim=32
    )(director)

    director = layers.Flatten()(director)

    writer_lookup = layers.IntegerLookup(
        vocabulary=df["writer_id"].unique(),
        mask_token=None
    )

    writer = writer_lookup(writer_input)

    writer = layers.Embedding(
        input_dim=writer_lookup.vocabulary_size(),
        output_dim=32
    )(writer)

    writer = layers.Flatten()(writer)

    producer_lookup = layers.IntegerLookup(
        vocabulary=df["producer_id"].unique(),
        mask_token=None
    )

    producer = producer_lookup(producer_input)

    producer = layers.Embedding(
        input_dim=producer_lookup.vocabulary_size(),
        output_dim=32
    )(producer)

    producer = layers.Flatten()(producer)

    user_lookup = layers.IntegerLookup(
        vocabulary=df["user_id"].unique(),
        mask_token=None
    )

    user = user_lookup(user_input)

    user = layers.Embedding(
        input_dim=user_lookup.vocabulary_size(),
        output_dim=32
    )(user)

    user = layers.Flatten()(user)

    movie_lookup = layers.IntegerLookup(
        vocabulary=df["movie_id"].unique(),
        mask_token=None
    )

    movie = movie_lookup(movie_input)

    movie = layers.Embedding(
        input_dim=movie_lookup.vocabulary_size(),
        output_dim=32
    )(movie)

    movie = layers.Flatten()(movie)

    # ---------- Multi Embeddings ----------

    favorite_director_lookup = layers.IntegerLookup(
        vocabulary=df["favorite_directors"].explode().unique(),
        mask_token=None
    )

    favorite_directors = favorite_director_lookup(
        favorite_directors_input
    )

    favorite_directors = layers.Embedding(
        input_dim=favorite_director_lookup.vocabulary_size(),
        output_dim=32,
        mask_zero=True
    )(favorite_directors)

    favorite_writer_lookup = layers.IntegerLookup(
        vocabulary=df["favorite_writers"].explode().unique(),
        mask_token=None
    )

    favorite_writers = favorite_writer_lookup(
        favorite_writers_input
    )

    favorite_writers = layers.Embedding(
        input_dim=favorite_writer_lookup.vocabulary_size(),
        output_dim=32,
        mask_zero=True
    )(favorite_writers)

    genre_lookup = layers.IntegerLookup(
        vocabulary=df["genres"].explode().unique(),
        mask_token=None
    )

    genres = genre_lookup(genres_input)

    genres = layers.Embedding(
        input_dim=genre_lookup.vocabulary_size(),
        output_dim=16,
        mask_zero=True
    )(genres)

    favorite_genres = genre_lookup(favorite_genres_input)

    favorite_genres = layers.Embedding(
        input_dim=genre_lookup.vocabulary_size(),
        output_dim=16,
        mask_zero=True
    )(favorite_genres)

    # ---------- Merge ----------

    x = layers.Concatenate()([
        numeric,
        genres,
        favorite_genres,
        bool_input,
        country,
        director,
        writer,
        producer,
        favorite_directors,
        favorite_writers,
        user,
        movie,
    ])

    # ---------- Dense ----------

    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Dense(64, activation="relu")(x)

    output = layers.Dense(
        1,
        activation="linear",
        name="target_score"
    )(x)

    model = Model(
        inputs=[
            numeric_input,
            country_input,
            director_input,
            writer_input,
            producer_input,
            favorite_directors_input,
            favorite_writers_input,
            genres_input,
            favorite_genres_input,
            bool_input,
            user_input,
            movie_input,
        ],
        outputs=output,
    )

    return model
