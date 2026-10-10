from sqlalchemy import text
from typing import List
from ..database.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class InteractionRepository:
    """
    Repository used for giving interaction data form DataBase.
    """

    def __init__(self, session: AsyncSession):
        """
        init method used for creating variables.
        """
        self.session = session

    async def get_user_interactions(self, user_id: int) -> List[dict]:
        """
        method used for collecting user interactions from DataBase.
        """
        query = text("""
                     SELECT movie_id,
                            interaction_type,
                            weight, timestamp
                     FROM analytics_interaction
                     WHERE user_id = :user_id
                     ORDER BY timestamp DESC
                     """)  # get interactions

        result = await self.session.execute(query, {"user_id": user_id})
        rows = result.mappings().all()

        return [dict(row) for row in rows]

    async def get_movie_popularity(self, movie_id: int) -> int:
        """
        method used for collecting movie interactions length from DataBase.
        """

        query = text("""
                     SELECT COUNT(*)
                     FROM analytics_interaction
                     WHERE movie_id = :movie_id
                     """)  # get length

        result = await self.session.execute(query, {"movie_id": movie_id})
        return result.scalar_one()


def get_intraction_repository(session: AsyncSession = Depends(get_session)):
    """
    function used for return InteractionRepository instance.
    """
    return InteractionRepository(session)
