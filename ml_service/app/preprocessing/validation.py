import numpy as np
import pandas as pd


def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    allowed_object_columns = {
        "favorite_directors",
        "favorite_writers",
    }

    if df.isnull().values.any():
        null_columns = df.columns[df.isnull().any()].tolist()
        raise ValueError(
            f"Dataset contains missing values in columns: {null_columns}"
        )

    if not df.index.is_unique:
        raise ValueError("Dataset index contains duplicate values.")

    object_columns = set(
        df.select_dtypes(include=["object"]).columns
    )

    invalid_columns = object_columns - allowed_object_columns

    if invalid_columns:
        raise ValueError(
            f"Unexpected object columns found: {sorted(invalid_columns)}"
        )

    for column in allowed_object_columns:
        if not df[column].apply(lambda x: isinstance(x, list)).all():
            raise ValueError(
                f"Column '{column}' must contain only lists."
            )

    datetime_columns = df.select_dtypes(
        include=["datetime64[ns]", "datetimetz"]
    ).columns.tolist()

    if datetime_columns:
        raise ValueError(
            f"Datetime columns found: {datetime_columns}"
        )

    numeric_df = df.select_dtypes(include=np.number)

    if np.isinf(numeric_df.to_numpy()).any():
        raise ValueError(
            "Dataset contains infinity values."
        )

    return df
