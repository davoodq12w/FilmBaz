from pathlib import Path
import json
import os
from datetime import date
import glob

BASE_DIR = Path(__file__).resolve().parent.parent

def get_latest_raw_dataset():
    dataset_dir = BASE_DIR / "datasets" / "raw"
    files = sorted(dataset_dir.glob("dataset_*.csv"))

    if not files:
        raise FileNotFoundError("No dataset found.")

    return files[-1]


def get_latest_processed_dataset():
    dataset_dir = BASE_DIR / "datasets" / "processed"
    files = sorted(dataset_dir.glob("dataset_*.csv"))

    if not files:
        raise FileNotFoundError("No dataset found.")

    return files[-1]


def save_training_log(log_data: dict):
    log_file = BASE_DIR / "logs" / "training_logs.json"
    os.makedirs("logs", exist_ok=True)
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_data)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)


def create_model_metadata(history, results):
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
    json_files = glob.glob("../saved_models/*.json")
    if not json_files:
        return None, None
    json_path = json_files[0]
    with open(json_path, "r", encoding="utf8") as f:
        metadata = json.load(f)
    return metadata, json_path


def is_better(new_meta, old_meta):
    if old_meta is None:
        return True
    return (
            new_meta["best_val_rmse"]
            < old_meta["best_val_rmse"]
    )


def delete_old_model():
    for file in glob.glob("../saved_models/*"):
        os.remove(file)


def save_best_model(model, metadata):
    os.makedirs("models", exist_ok=True)
    delete_old_model()

    today = str(date.today())
    model_path = f"models/recommender_{today}.keras"
    json_path = f"models/recommender_{today}.json"

    model.save(model_path)

    with open(json_path, "w", encoding="utf8") as f:
        json.dump(metadata, f, indent=4)
