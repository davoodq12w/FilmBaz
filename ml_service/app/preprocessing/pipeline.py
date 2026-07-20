from pathlib import Path
from datetime import datetime
import pandas as pd
from utils import get_latest_raw_dataset
from .clean import cleaned_data
from .feature_engineering import encode_genres, create_last_interaction_feature, encode_country
from .scaling import normalize_features
from .validation import validate_dataset

PROCESSED_DATASET_DIR = Path("../../datasets/processed")


def get_processed_dataset() -> pd.DataFrame:
    df = pd.read_csv(get_latest_raw_dataset())
    df = cleaned_data(df)
    df = create_last_interaction_feature(df)
    df = encode_genres(df)
    df = encode_country(df)
    df = normalize_features(df)

    validate_dataset(df)

    PROCESSED_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROCESSED_DATASET_DIR / f"dataset_{timestamp}.csv"
    df.to_csv(output_path, index=False)

    return df
