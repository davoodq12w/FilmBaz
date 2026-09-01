from fastapi import APIRouter, Depends, Header, HTTPException, status
from ..inference.predictor import get_recommender, RecommenderMovies
from pydantic import BaseModel
from ..preprocessing.pipeline import get_processed_dataset
from ..training.trainer import train_model
import hashlib
import hmac
import time
from decouple import config
from ..main import load_recommendation_model

router = APIRouter()
BUILD_MODEL_PASSWORD = config("BUILD_MODEL_PASSWORD")
MAX_TIME_DIFF = 300  # 5 minutes


class DataInput(BaseModel):
    user_id: int
    movie_ids: list[int]


@router.post("/recomendation/get_movies/")
async def get_recommendation(data: DataInput, recommender: RecommenderMovies = Depends(get_recommender)):
    result = await recommender.predict(data.user_id, data.movie_ids)
    return result


@router.get("/build_model/")
def build_model():
    get_processed_dataset()
    train_model()
    load_recommendation_model()

#
# @router.post("/build_model/")
# def build_model(
#         x_timestamp: str = Header(...),
#         x_signature: str = Header(...),
# ):
#     # بررسی معتبر بودن Timestamp
#     try:
#         timestamp = int(x_timestamp)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid timestamp",
#         )
#
#     if abs(int(time.time()) - timestamp) > MAX_TIME_DIFF:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Expired request",
#         )
#
#     # ساخت امضای مورد انتظار
#     message = f"POST\n/build_model/\n{x_timestamp}"
#
#     expected_signature = hmac.new(
#         BUILD_MODEL_PASSWORD.encode(),
#         message.encode(),
#         hashlib.sha256,
#     ).hexdigest()
#
#     # مقایسه امضا
#     if not hmac.compare_digest(x_signature, expected_signature):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid signature",
#         )
#
#     # درخواست معتبر است
#     get_processed_dataset()
#     train_model()
#     load_recommendation_model()
#
#     return {
#         "message": "Model built successfully"
#     }
