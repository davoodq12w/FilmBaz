import tensorflow as tf
from tensorflow.keras import layers, Model

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

def build_model(normalizer, vocabularies):
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
    numeric = normalizer(numeric_input)

    # ---------- Single Embeddings ----------
    country_lookup = layers.StringLookup(
        vocabulary=vocabularies["country"],
        mask_token=None
    )

    country = country_lookup(country_input)

    country = layers.Embedding(
        input_dim=country_lookup.vocabulary_size(),
        output_dim=16
    )(country)

    country = layers.Flatten()(country)

    director_lookup = layers.IntegerLookup(
        vocabulary=vocabularies["director_id"],
        mask_token=None
    )

    director = director_lookup(director_input)

    director = layers.Embedding(
        input_dim=director_lookup.vocabulary_size(),
        output_dim=32
    )(director)

    director = layers.Flatten()(director)

    writer_lookup = layers.IntegerLookup(
        vocabulary=vocabularies["writer_id"],
        mask_token=None
    )

    writer = writer_lookup(writer_input)

    writer = layers.Embedding(
        input_dim=writer_lookup.vocabulary_size(),
        output_dim=32
    )(writer)

    writer = layers.Flatten()(writer)

    producer_lookup = layers.IntegerLookup(
        vocabulary=vocabularies["producer_id"],
        mask_token=None
    )

    producer = producer_lookup(producer_input)

    producer = layers.Embedding(
        input_dim=producer_lookup.vocabulary_size(),
        output_dim=32
    )(producer)

    producer = layers.Flatten()(producer)

    user_lookup = layers.IntegerLookup(
        vocabulary=vocabularies["user_id"],
        mask_token=None
    )

    user = user_lookup(user_input)

    user = layers.Embedding(
        input_dim=user_lookup.vocabulary_size(),
        output_dim=32
    )(user)

    user = layers.Flatten()(user)

    movie_lookup = layers.IntegerLookup(
        vocabulary=vocabularies["movie_id"],
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
        vocabulary=vocabularies["favorite_directors"],
        mask_token=None
    )
    favorite_directors = favorite_director_lookup(
        favorite_directors_input
    )
    favorite_directors = layers.Embedding(
        input_dim=favorite_director_lookup.vocabulary_size(),
        output_dim=32,
        mask_zero=True,
    )(favorite_directors)
    favorite_directors = layers.GlobalAveragePooling1D()(
        favorite_directors
    )

    favorite_writer_lookup = layers.IntegerLookup(
        vocabulary=vocabularies["favorite_writers"],
        mask_token=None
    )
    favorite_writers = favorite_writer_lookup(
        favorite_writers_input
    )
    favorite_writers = layers.Embedding(
        input_dim=favorite_writer_lookup.vocabulary_size(),
        output_dim=32,
        mask_zero=True,
    )(favorite_writers)
    favorite_writers = layers.GlobalAveragePooling1D()(
        favorite_writers
    )

    genre_lookup = layers.IntegerLookup(
        vocabulary=vocabularies["genres"],
        mask_token=None
    )
    genres = genre_lookup(genres_input)
    genres = layers.Embedding(
        input_dim=genre_lookup.vocabulary_size(),
        output_dim=16,
        mask_zero=True,
    )(genres)
    genres = layers.GlobalAveragePooling1D()(genres)

    favorite_genres = genre_lookup(favorite_genres_input)
    favorite_genres = layers.Embedding(
        input_dim=genre_lookup.vocabulary_size(),
        output_dim=16,
        mask_zero=True,
    )(favorite_genres)
    favorite_genres = layers.GlobalAveragePooling1D()(
        favorite_genres
    )

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
