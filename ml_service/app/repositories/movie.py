from sqlalchemy import text
from typing import List, Dict, Optional
from ..database.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class MovieRepository:
    """
    Repository used for giving data of movies.
    """

    def __init__(self, session: AsyncSession):
        """
        init method used for creating variables.
        """
        self.session = session

    async def get_movie_basic(self, movie_id: int) -> Optional[dict]:
        """
        method used for collecting basic information about a movie from DataBase.
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
                     """) # get movie data

        result = await self.session.execute(query, {"movie_id": movie_id})
        row = result.mappings().first()

        return dict(row) if row else None

    async def get_movies_basic(self, movie_ids: List[int]) -> List[dict]:
        """
        method used for collecting basic information about movies from DataBase.
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
                     """) # get movies data

        result = await self.session.execute(query, {"movie_ids": movie_ids})
        rows = result.mappings().all()

        return [dict(row) for row in rows]


class MovieRelationRepository:
    """
    Repository used for giving data of movie relations.
    """
    def __init__(self, session: AsyncSession):
        """
        init method used for creating variables.
        """
        self.session = session

    async def get_movie_genres(self, movie_id: int) -> List[dict]:
        """
        method used for collecting information genres of a movie from DataBase.
        """
        query = text("""
                     SELECT g.id AS genre_id
                     FROM film_movie_genres mg
                              JOIN film_genre g ON g.id = mg.genre_id
                     WHERE mg.movie_id = :movie_id
                     """) # get genres

        result = await self.session.execute(query, {"movie_id": movie_id})
        return list(result.scalars().all())

    async def get_movies_genres(self, movie_ids: List[int]) -> Dict[int, List[dict]]:
        """
        method used for collecting information genres of movies from DataBase.
        """
        if not movie_ids:
            return {}

        query = text("""
                     SELECT mg.movie_id,
                            g.id AS genre_id
                     FROM film_movie_genres mg
                              JOIN film_genre g ON g.id = mg.genre_id
                     WHERE mg.movie_id = ANY (:movie_ids)
                     """) # get genres

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
        method used for collecting information crews of a movie from DataBase.
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
        method used for collecting information crews of movies from DataBase.
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
        method used for collecting crew ids of movie form DataBase.
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
    """
    function used for return MovieRepository instance.
    """
    return MovieRepository(session)


def get_movie_relation_repository(session: AsyncSession = Depends(get_session)):
    """
    function used for return MovieRelationRepository instance.
    """
    return MovieRelationRepository(session)
