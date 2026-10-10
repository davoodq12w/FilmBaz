from ..repositories.user import get_user_repository, UserRepository
from fastapi import Depends
from datetime import datetime
from zoneinfo import ZoneInfo


class UserService:
    """
    Service used for giving user information
    """

    def __init__(self, repo: UserRepository):
        """
        init method used for creating variables.
        """
        self.repo = repo

    def padding_to_5(self, lst: list):
        """
        method used for making sure are list lenght are 5.
        """
        return lst[:5] + [0] * max(0, 5 - len(lst))

    async def build_user_features(self, user_id: int):
        """
        method used for collecting user information.
        """
        user = await self.repo.get_user_basic(user_id)  # get used object.
        favorite_genres = await self.repo.get_user_favorite_genres(user_id)
        favorite_genres = self.padding_to_5(favorite_genres)  # padding genres to 5
        now = datetime.now(tz=ZoneInfo("Asia/Tehran"))
        created = user["created"]

        data = {
            "user_id": user_id,
            "account_age_days": (now - created).days,
            "favorite_genres": favorite_genres
        }
        return data


def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    """
    function used rerurn UserService instance.
    """
    return UserService(repo)
