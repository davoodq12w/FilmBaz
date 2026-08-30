from ..repositories.user import get_user_repository, UserRepository
from fastapi import Depends
from datetime import datetime
from zoneinfo import ZoneInfo


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def padding_to_5(self, lst: list):
        return lst[:5] + [0] * max(0, 5 - len(lst))

    async def build_user_features(self, user_id: int):
        user = await self.repo.get_user_basic(user_id)
        favorite_genres = await self.repo.get_user_favorite_genres(user_id)
        favorite_genres = self.padding_to_5(favorite_genres)
        now = datetime.now(tz=ZoneInfo("Asia/Tehran"))
        created = user["created"]

        data = {
            "user_id": user_id,
            "account_age_days": (now - created).days,
            "favorite_genres": favorite_genres
        }
        return data


def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo)
