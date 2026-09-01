from sklearn.model_selection import train_test_split
from ..utils import (
    get_latest_processed_dataset,
    create_model_metadata,
    get_current_best_metadata,
    is_better,
    save_training_log,
    save_best_model
)
import pandas as pd
from ast import literal_eval
from tensorflow.keras import layers
from ..models.recommender import NUMERIC_COLUMNS, build_model
import numpy as np
import tensorflow as tf


def get_df():
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
    return df


def dataframe_to_inputs(df):
    inputs = {
        "numeric_features": df[NUMERIC_COLUMNS].astype("float32").values,
        "country": tf.constant(
            df["country"].astype(str).values,
            dtype=tf.string
        ),
        "director_id": df["director_id"].astype("int32").values,
        "writer_id": df["writer_id"].astype("int32").values,
        "producer_id": df["producer_id"].astype("int32").values,
        "favorite_directors": np.array(df["favorite_directors"].tolist(), dtype=np.int32),
        "favorite_writers": np.array(df["favorite_writers"].tolist(), dtype=np.int32),
        "genres": np.array(df["genres"].tolist(), dtype=np.int32),
        "favorite_genres": np.array(df["favorite_genres"].tolist(), dtype=np.int32),
        "bool_features": df[["is_series", "adult"]].astype("float32").values,
        "user_id": df["user_id"].astype("int32").values,
        "movie_id": df["movie_id"].astype("int32").values,
    }
    return inputs


def train_model():
    df = get_df()

    fetures = df.drop(["target_score"], axis=1)
    target = df["target_score"]
    x_train, x_test, y_train, y_test = train_test_split(fetures, target, test_size=0.2, random_state=42)

    normalizer = layers.Normalization()

    normalizer.adapt(
        x_train[NUMERIC_COLUMNS].to_numpy(dtype="float32")
    )

    vocabularies = {
        "user_id": x_train["user_id"].unique(),
        "movie_id": x_train["movie_id"].unique(),
        "director_id": x_train["director_id"].unique(),
        "writer_id": x_train["writer_id"].unique(),
        "producer_id": x_train["producer_id"].unique(),
        "country": x_train["country"].astype(str).unique().tolist(),
        "favorite_directors": x_train["favorite_directors"].explode().unique().astype("int32"),
        "favorite_writers": x_train["favorite_writers"].explode().unique().astype("int32"),
        "genres": x_train["genres"].explode().unique().astype("int32"),
    }

    model = build_model(normalizer, vocabularies)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-3
        ),
        loss="mse",
        metrics=[
            tf.keras.metrics.MeanAbsoluteError(name="mae"),
            tf.keras.metrics.RootMeanSquaredError(name="rmse"),
        ]
    )

    train_inputs = dataframe_to_inputs(x_train)
    test_inputs = dataframe_to_inputs(x_test)

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True,
    )

    history = model.fit(
        train_inputs,
        y_train.astype("float32").values,
        validation_data=(
            test_inputs,
            y_test.astype("float32").values,
        ),
        epochs=20,
        batch_size=256,
        verbose=1,
        callbacks=[early_stopping],
    )

    results = model.evaluate(
        test_inputs,
        y_test.astype("float32").values,
        verbose=1,
    )

    metadata = create_model_metadata(
        history,
        results,
    )

    old_metadata, _ = get_current_best_metadata()

    better = is_better(
        metadata,
        old_metadata,
    )

    save_training_log({
        **metadata,
        "saved": better,
    })

    if better:
        save_best_model(
            model,
            metadata,
        )
