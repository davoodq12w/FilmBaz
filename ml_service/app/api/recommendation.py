from fastapi import APIRouter, Depends, HTTPException
from ..repositories.user import get_user_repository, UserRepository

router = APIRouter()


@router.get("/recomendation/get_movies/{user_id}")
async def get_recommendation(user_id: int, repo: UserRepository = Depends(get_user_repository), ):
    user = await repo.get_user_basic(user_id)
    return user
