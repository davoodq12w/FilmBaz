from sqlalchemy import text
from typing import List, Dict, Optional
from ..database.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class MovieRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_movie_basic(self, movie_id: int) -> Optional[dict]:
        """
        اطلاعات پایه یک فیلم را برمی‌گرداند
        """
        query = text("""
                     SELECT id AS movie_id,
                            runtime,
                            rate,
                            country,
                            is_serie,
                            adult,
                            release_date
                     FROM film_movie
                     WHERE id = :movie_id
                     """)

        result = await self.session.execute(query, {"movie_id": movie_id})
        row = result.mappings().first()

        return dict(row) if row else None

    async def get_movies_basic(self, movie_ids: List[int]) -> List[dict]:
        """
        اطلاعات پایه چندین فیلم را یکجا برمی‌گرداند
        (برای ساخت دیتاست توصیه مفید است)
        """
        if not movie_ids:
            return []

        query = text("""
                     SELECT id AS movie_id,
                            runtime,
                            rate,
                            country,
                            is_serie,
                            adult,
                            release_date
                     FROM film_movie
                     WHERE id = ANY (:movie_ids)
                     """)

        result = await self.session.execute(query, {"movie_ids": movie_ids})
        rows = result.mappings().all()

        return [dict(row) for row in rows]


class MovieRelationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_movie_genres(self, movie_id: int) -> List[dict]:
        """
        ژانرهای یک فیلم را برمی‌گرداند
        """
        query = text("""
                     SELECT g.id AS genre_id
                     FROM film_movie_genres mg
                              JOIN film_genre g ON g.id = mg.genre_id
                     WHERE mg.movie_id = :movie_id
                     """)

        result = await self.session.execute(query, {"movie_id": movie_id})
        return list(result.scalars().all())

    async def get_movies_genres(self, movie_ids: List[int]) -> Dict[int, List[dict]]:
        """
        ژانرهای چندین فیلم را یکجا برمی‌گرداند
        خروجی: {movie_id: [genre_dicts]}
        """
        if not movie_ids:
            return {}

        query = text("""
                     SELECT mg.movie_id,
                            g.id AS genre_id
                     FROM film_movie_genres mg
                              JOIN film_genre g ON g.id = mg.genre_id
                     WHERE mg.movie_id = ANY (:movie_ids)
                     """)

        result = await self.session.execute(query, {"movie_ids": movie_ids})
        rows = result.mappings().all()

        genres_map: Dict[int, List[dict]] = {mid: [] for mid in movie_ids}
        for row in rows:
            genres_map[row["movie_id"]].append({
                "genre_id": row["genre_id"],
            })

        return genres_map

    async def get_movie_crews(self, movie_id: int) -> List[dict]:
        """
        خدمه یک فیلم (کارگردان، نویسنده، تهیه‌کننده) را برمی‌گرداند
        """
        query = text("""
                     SELECT mc.role,
                            c.id AS crew_id
                     FROM people_moviecrew mc
                              JOIN people_crewmember c ON c.id = mc.crew_id
                     WHERE mc.movie_id = :movie_id
                       AND mc.role IN ('director', 'writer', 'producer')
                     """)

        result = await self.session.execute(query, {"movie_id": movie_id})
        rows = result.mappings().all()

        return [dict(row) for row in rows]

    async def get_movies_crews(self, movie_ids: List[int]) -> Dict[int, List[dict]]:
        """
        خدمه چندین فیلم را یکجا برمی‌گرداند
        خروجی: {movie_id: [crew_dicts]}
        """
        if not movie_ids:
            return {}

        query = text("""
                     SELECT mc.movie_id,
                            mc.role,
                            c.id AS crew_id
                     FROM people_moviecrew mc
                              JOIN people_crewmember c ON c.id = mc.crew_id
                     WHERE mc.movie_id = ANY (:movie_ids)
                       AND mc.role IN ('director', 'writer', 'producer')
                     """)

        result = await self.session.execute(query, {"movie_ids": movie_ids})
        rows = result.mappings().all()

        crews_map: Dict[int, List[dict]] = {mid: [] for mid in movie_ids}
        for row in rows:
            crews_map[row["movie_id"]].append({
                "role": row["role"],
                "crew_id": row["crew_id"],
            })

        return crews_map

    async def get_movie_director_writer_producer(self, movie_id: int) -> dict:
        """
        به صورت خلاصه director_id, writer_id, producer_id را برمی‌گرداند
        (اگر چند نفر باشند، اولین نفر را برمی‌دارد)
        """
        crews = await self.get_movie_crews(movie_id)

        result = {
            "director_id": None,
            "writer_id": None,
            "producer_id": None,
        }

        for crew in crews:
            role = crew["role"]
            if role == "director" and result["director_id"] is None:
                result["director_id"] = crew["crew_id"]
            elif role == "writer" and result["writer_id"] is None:
                result["writer_id"] = crew["crew_id"]
            elif role == "producer" and result["producer_id"] is None:
                result["producer_id"] = crew["crew_id"]

        return result


def get_movie_repository(session: AsyncSession = Depends(get_session)):
    return MovieRepository(session)


def get_movie_relation_repository(session: AsyncSession = Depends(get_session)):
    return MovieRelationRepository(session)