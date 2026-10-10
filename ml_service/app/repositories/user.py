from sqlalchemy import text
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.session import get_session
from fastapi import Depends


class UserRepository:
    """
    Repository used for giving user information from DataBase.
    """

    def __init__(self, session: AsyncSession):
        """
        init method used for creating variables.
        """
        self.session = session

    async def get_user_basic(self, user_id: int) -> Optional[dict]:
        """
        method used for reading user information from DataBase by SQL.
        """
        query = text("""
                     SELECT id AS user_id, created
                     FROM account_filmbazuser
                     WHERE id = :user_id
                     """)  # get user information.

        result = await self.session.execute(query, {"user_id": user_id})  # run the query
        row = result.mappings().first()

        return dict(row) if row else None

    async def get_user_favorite_genres(self, user_id: int) -> list[dict]:
        """
        method used for reading user favorite genres from DataBase by SQL.
        """

        query = text("""
                     SELECT genre_id
                     FROM account_filmbazuser_favorite_genres
                     WHERE filmbazuser_id = :user_id
                     """)  # get genres.

        result = await self.session.execute(query, {"user_id": user_id})
        return list(result.scalars().all())


def get_user_repository(session: AsyncSession = Depends(get_session)):
    """
    function used for return UserRepository instance.
    """
    return UserRepository(session)
