from fastapi import FastAPI
from .api import recommendation
from tensorflow.keras.models import load_model
from pathlib import Path

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
app.include_router(recommendation.router, tags=["recommendation"])


def load_recommendation_model():
    app.state.recommender_model = load_model(
        f"{BASE_DIR}/models/recommender.keras"
    )
