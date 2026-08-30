from app.services.movie import MovieService, get_movie_service
from app.services.user import UserService, get_user_service
from app.services.interaction import InteractionService, get_interaction_service
from fastapi import Depends


class RowData:
    def __init__(
            self,
            user_service: UserService,
            interaction_service: InteractionService,
            movie_service: MovieService
    ):
        self.user_service = user_service
        self.interaction_service = interaction_service
        self.movie_service = movie_service

    async def get_raw_data(self, user_id: int, movie_ids: list[int]):
        user_fetures = await self.user_service.build_user_features(user_id=user_id)
        interactions = await self.interaction_service.get_interactions(user_id=user_id)
        movies = await self.movie_service.get_movies(movie_ids=movie_ids)
        data = {
            "user_fetures": user_fetures,
            "interactions": interactions,
            "movies": movies
        }
        return data


def row_data(
        user_service: UserService = Depends(get_user_service),
        interaction_service: InteractionService = Depends(get_interaction_service),
        movie_service: MovieService = Depends(get_movie_service),
):
    return RowData(user_service, interaction_service, movie_service)
