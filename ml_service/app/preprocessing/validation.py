import numpy as np
import pandas as pd


EXPECTED_OBJECT_TYPES = {
    "genres": list,
    "favorite_genres": list,
    "favorite_directors": list,
    "favorite_writers": list,
    "country": str,
}


def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    # =====================================================
    # Missing Values
    # =====================================================
    if df.isnull().values.any():
        null_columns = df.columns[df.isnull().any()].tolist()

        raise ValueError(
            f"Dataset contains missing values in columns: {null_columns}"
        )

    # =====================================================
    # Duplicate Index
    # =====================================================
    if not df.index.is_unique:
        raise ValueError(
            "Dataset index contains duplicate values."
        )

    # =====================================================
    # Validate Object Columns
    # =====================================================
    object_columns = set(
        df.select_dtypes(include=["object"]).columns
    )

    expected_columns = set(
        EXPECTED_OBJECT_TYPES.keys()
    )

    unexpected_columns = object_columns - expected_columns

    if unexpected_columns:
        raise ValueError(
            f"Unexpected object columns found: {sorted(unexpected_columns)}"
        )

    missing_columns = expected_columns - object_columns

    if missing_columns:
        raise ValueError(
            f"Expected object columns are missing: {sorted(missing_columns)}"
        )

    # =====================================================
    # Validate Object Types
    # =====================================================
    for column, expected_type in EXPECTED_OBJECT_TYPES.items():

        invalid = df[column].apply(
            lambda value: not isinstance(value, expected_type)
        )

        if invalid.any():
            invalid_value = df.loc[
                invalid,
                column
            ].iloc[0]

            raise ValueError(
                f"Column '{column}' must contain only "
                f"{expected_type.__name__}. "
                f"Found value {repr(invalid_value)} "
                f"of type {type(invalid_value).__name__}."
            )

    # =====================================================
    # Datetime Columns
    # =====================================================
    datetime_columns = df.select_dtypes(
        include=["datetime64[ns]", "datetimetz"]
    ).columns.tolist()

    if datetime_columns:
        raise ValueError(
            f"Unexpected datetime columns found: {datetime_columns}"
        )

    # =====================================================
    # Infinity Values
    # =====================================================
    numeric_df = df.select_dtypes(
        include=np.number
    )

    if np.isinf(
        numeric_df.to_numpy()
    ).any():
        raise ValueError(
            "Dataset contains infinity values."
        )

    # =====================================================
    # ID Validation
    # =====================================================
    id_columns = [
        "user_id",
        "movie_id",
    ]

    for column in id_columns:

        if (df[column] <= 0).any():

            invalid_count = int(
                (df[column] <= 0).sum()
            )

            raise ValueError(
                f"Column '{column}' contains "
                f"{invalid_count} invalid ids."
            )

    # =====================================================
    # Target Score Validation
    # =====================================================
    if (df["target_score"] < 0).any():

        invalid_count = int(
            (df["target_score"] < 0).sum()
        )

        raise ValueError(
            f"target_score contains "
            f"{invalid_count} negative values."
        )

    return df