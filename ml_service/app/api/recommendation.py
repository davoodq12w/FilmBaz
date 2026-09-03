from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from ..inference.predictor import get_recommender, RecommenderMovies
from pydantic import BaseModel
from ..preprocessing.pipeline import get_processed_dataset
from ..training.trainer import train_model
import hashlib
import hmac
import time
from decouple import config
from tensorflow.keras.models import load_model
from pathlib import Path

router = APIRouter()
BUILD_MODEL_PASSWORD = config("BUILD_MODEL_PASSWORD")
MAX_TIME_DIFF = 300  # 5 minutes
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class DataInput(BaseModel):
    user_id: int
    movie_ids: list[int]


@router.post("/recomendation/get_movies/")
async def get_recommendation(data: DataInput, recommender: RecommenderMovies = Depends(get_recommender)):
    result = await recommender.predict(data.user_id, data.movie_ids)
    return result


@router.post("/build_model/")
def build_model(
        requset: Request,
        x_timestamp: str = Header(...),
        x_signature: str = Header(...),
):
    try:
        timestamp = int(x_timestamp)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid timestamp",
        )

    if abs(int(time.time()) - timestamp) > MAX_TIME_DIFF:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired request",
        )

    message = f"POST\n/build_model/\n{x_timestamp}"

    expected_signature = hmac.new(
        BUILD_MODEL_PASSWORD.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(x_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    get_processed_dataset()
    train_model()
    requset.app.state.recommender_model = load_model(
        f"{BASE_DIR}/models/recommender.keras"
    )

    return {
        "message": "Model built successfully"
    }
