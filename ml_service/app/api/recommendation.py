from fastapi import APIRouter, Depends, HTTPException
from app.services.raw_data import row_data, RowData
from pydantic import BaseModel

router = APIRouter()


class DataInput(BaseModel):
    user_id: int
    movie_ids: list[int]


@router.post("/recomendation/get_movies/")
async def get_recommendation(data: DataInput, service: RowData = Depends(row_data)):
    result = await service.get_raw_data(user_id=data.user_id, movie_ids=data.movie_ids)
    return result
