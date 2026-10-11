from pathlib import Path
import json
import os
from datetime import date
import glob

BASE_DIR = Path(__file__).resolve().parent.parent


def get_latest_raw_dataset():
    """
    function used for returning the latest raw dataset file.
    """
    dataset_dir = BASE_DIR / "datasets" / "raw"
    files = sorted(dataset_dir.glob("dataset_*.csv"))

    if not files:
        raise FileNotFoundError("No dataset found.")

    return files[-1]


def get_latest_processed_dataset():
    """
    function used for returning the latest processed dataset file.
    """
    dataset_dir = BASE_DIR / "datasets" / "processed"
    files = sorted(dataset_dir.glob("dataset_*.csv"))

    if not files:
        raise FileNotFoundError("No dataset found.")

    return files[-1]


def delete_older_processed_dataset():
    """
    function used for deleting the older processed dataset files.
    """
    dataset_dir = BASE_DIR / "datasets" / "processed"
    files = dataset_dir.glob("dataset_*.csv")

    if not files:
        pass
    else:
        for file in files:
            os.remove(file)


def save_training_log(log_data: dict):
    """
    function used for saving training logs of recommendation model.
    """
    log_file = BASE_DIR / "logs" / "training_logs.json"
    os.makedirs("logs", exist_ok=True)

    # if file exists add log to it else create the file.
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_data)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)


def create_model_metadata(history, results):
    """
    function used for returning the model metadata.
    """
    return {
        "date": str(date.today()),
        "loss": float(results[0]),
        "mae": float(results[1]),
        "rmse": float(results[2]),
        "best_val_loss": float(min(history.history["val_loss"])),
        "best_val_mae": float(min(history.history["val_mae"])),
        "best_val_rmse": float(min(history.history["val_rmse"])),
        "epochs": len(history.history["loss"]),
    }


def get_current_best_metadata():
    """
    function used for returning the best metadata of model for right now.
    """
    json_files = glob.glob("../models/*.json")
    if not json_files:
        return None, None
    json_path = json_files[0]
    with open(json_path, "r", encoding="utf8") as f:
        metadata = json.load(f)
    return metadata, json_path


def is_better(new_meta, old_meta):
    """
    function used for Compare the recommendation models.
    """
    if old_meta is None:
        return True
    return (
            new_meta["best_val_rmse"]
            < old_meta["best_val_rmse"]
    )


def delete_old_model():
    """
    function used for deleting old recommendation model and metadata of this.
    """
    for file in glob.glob("../models/*"):
        os.remove(file)


def save_best_model(model, metadata):
    """
    function used for saving best recommendation model.
    """
    os.makedirs("models", exist_ok=True)
    delete_old_model()

    model_path = f"models/recommender.keras"
    json_path = f"models/recommender.json"

    model.save(model_path)

    with open(json_path, "w", encoding="utf8") as f:
        json.dump(metadata, f, indent=4)

    print("recommender model saved.")
