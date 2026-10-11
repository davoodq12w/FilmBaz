from pathlib import Path
from datetime import datetime
import pandas as pd
from ..utils import get_latest_raw_dataset, delete_older_processed_dataset
from .clean import cleaned_data
from .validation import validate_dataset

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATASET_DIR = BASE_DIR / "datasets" / "processed"


def get_processed_dataset(df=None) -> Path | pd.DataFrame:
    """
    function used to run the preprocessing pipeline.
    steps: 1 load raw dataset 2 clean dataframe 3 validate dataframe
    4 if dataframe is load from file return path else return dataframe.
    """

    print("Loading raw dataset...")

    # checking to it's recive a dataframe or not.
    df_is_input = False
    if df is not None:
        df_is_input = True

    # if it is not recive a dataframe we load it from file.
    if not df_is_input:
        df = pd.read_csv(get_latest_raw_dataset())

    print("Cleaning dataset...")
    # step 2
    df = cleaned_data(df)

    print("Validating dataset...")
    # step 3
    validate_dataset(df)

    # step 4
    if not df_is_input:
        PROCESSED_DATASET_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = PROCESSED_DATASET_DIR / f"dataset_{timestamp}.csv"
        delete_older_processed_dataset()
        print(f"Processed dataset saved to {output_path}")
        df.to_csv(output_path, index=False)
        return output_path
    else:
        return df
