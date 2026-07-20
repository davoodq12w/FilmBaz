from pathlib import Path


def get_latest_raw_dataset():
    dataset_dir = Path("../../datasets/raw/")
    files = sorted(dataset_dir.glob("dataset_*.csv"))

    if not files:
        raise FileNotFoundError("No dataset found.")

    return files[-1]

def get_latest_processed_dataset():
    dataset_dir = Path("../../datasets/processed/")
    files = sorted(dataset_dir.glob("dataset_*.csv"))

    if not files:
        raise FileNotFoundError("No dataset found.")

    return files[-1]