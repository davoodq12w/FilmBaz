from app.repositories.movie import (
    get_movie_repository,
    get_movie_relation_repository,
    MovieRelationRepository,
    MovieRepository
)
from fastapi import Depends


class MovieService:
    def __init__(
            self,
            movie_repo: MovieRepository,
            rels_repo: MovieRelationRepository
    ):
        self.movie_repo = movie_repo
        self.rels_repo = rels_repo

    async def get_movies(self, movie_ids: list):
        movies = []
        for movie_id in movie_ids:
            movie = await self.movie_repo.get_movie_basic(movie_id)
            movie_genres = await self.rels_repo.get_movie_genres(movie_id)
            movie_crews = await self.rels_repo.get_movie_director_writer_producer(movie_id)
            movie_data = {
                **movie,
                **movie_crews,
                "genres": movie_genres,
            }
            movies.append(movie_data)

        return movies


def get_movie_service(
        movie_repo: MovieRepository = Depends(get_movie_repository),
        rels_repo: MovieRelationRepository = Depends(get_movie_relation_repository)
):
    return MovieService(movie_repo, rels_repo)
