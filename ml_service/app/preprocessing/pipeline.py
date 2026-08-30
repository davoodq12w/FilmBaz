from pathlib import Path
from datetime import datetime
import pandas as pd
from app.utils import get_latest_raw_dataset
from .clean import cleaned_data
from .validation import validate_dataset

PROCESSED_DATASET_DIR = Path("../../datasets/processed")


def get_processed_dataset() -> Path:
    print("Loading raw dataset...")
    df = pd.read_csv(get_latest_raw_dataset())

    print("Cleaning dataset...")
    df = cleaned_data(df)

    print("Validating dataset...")
    validate_dataset(df)

    PROCESSED_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PROCESSED_DATASET_DIR / f"dataset_{timestamp}.csv"

    print(f"Processed dataset saved to {output_path}")
    df.to_csv(output_path, index=False)

    return output_path

