from sqlalchemy import text
from typing import List
from ..database.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class InteractionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_interactions(self, user_id: int) -> List[dict]:
        """
        تمام تعاملات کاربر را برمی‌گرداند (داده خام)
        """
        query = text("""
                     SELECT movie_id,
                            interaction_type,
                            weight, timestamp
                     FROM analytics_interaction
                     WHERE user_id = :user_id
                     ORDER BY timestamp DESC
                     """)

        result = await self.session.execute(query, {"user_id": user_id})
        rows = result.mappings().all()

        return [dict(row) for row in rows]

    async def get_movie_popularity(self, movie_id: int) -> int:
        """
        تمام تعاملات یک فیلم را برمی گرداند
        """

        query = text("""
                     SELECT COUNT(*)
                     FROM analytics_interaction
                     WHERE movie_id = :movie_id
                     """)

        result = await self.session.execute(query, {"movie_id": movie_id})
        return result.scalar_one()



def get_intraction_repository(session: AsyncSession = Depends(get_session)):
    return InteractionRepository(session)