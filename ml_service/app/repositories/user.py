from sqlalchemy import text
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.session import get_session
from fastapi import Depends


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_basic(self, user_id: int) -> Optional[dict]:
        """
        فقط فیلدهای مورد نیاز برای feature engineering:
        - user_id
        - created
        """
        query = text("""
                     SELECT id AS user_id, created
                     FROM account_filmbazuser
                     WHERE id = :user_id
                     """)

        result = await self.session.execute(query, {"user_id": user_id})
        row = result.mappings().first()

        return dict(row) if row else None

    async def get_user_favorite_genres(self, user_id: int) -> list[dict]:
        """
        ژانر های مورد علاقه یک کاربر را بر میگرداند
        """

        query = text("""
                     SELECT genre_id
                     FROM account_filmbazuser_favorite_genres
                     WHERE filmbazuser_id = :user_id
                     """)

        result = await self.session.execute(query, {"user_id": user_id})
        return list(result.scalars().all())


def get_user_repository(session: AsyncSession = Depends(get_session)):
    return UserRepository(session)
