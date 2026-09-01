from fastapi import FastAPI
from .api import recommendation
from pathlib import Path
from tensorflow.keras.models import load_model
from .preprocessing.pipeline import get_processed_dataset
from .training.trainer import train_model

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

app.include_router(recommendation.router, tags=["recommendation"])


@app.on_event("startup")
def startup():
    try:
        app.state.recommender_model = load_model(
            f"{BASE_DIR}/models/recommender.keras"
        )
    except Exception as e:
        print(f"recommender model does not exists. Error:{e}")
        print("creating recommender model...")
        get_processed_dataset()
        train_model()
        app.state.recommender_model = load_model(
            f"{BASE_DIR}/models/recommender.keras"
        )
