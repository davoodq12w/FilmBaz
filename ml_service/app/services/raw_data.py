from ..services.movie import MovieService, get_movie_service
from ..services.user import UserService, get_user_service
from ..services.interaction import InteractionService, get_interaction_service
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
        user = await self.user_service.build_user_features(user_id=user_id)
        interaction = await self.interaction_service.get_interactions(user_id=user_id)
        movies = await self.movie_service.get_movies(movie_ids=movie_ids)

        data = []
        for movie in movies:
            row = {
                "user_id": user["user_id"],
                "movie_id": movie["movie_id"],
                "account_age_days": user["account_age_days"],
                "total_views": interaction["total_views"],
                "total_likes": interaction["total_likes"],
                "total_saves": interaction["total_saves"],
                "total_shares": interaction["total_shares"],
                "total_comments": interaction["total_comments"],
                "total_searches": interaction["total_searches"],
                "total_watches": interaction["total_watches"],
                "total_completes": interaction["total_completes"],
                "avg_interaction_weight": interaction["avg_interaction_weight"],
                "favorite_genres": user["favorite_genres"],
                "preferred_runtime": interaction["preferred_runtime"],
                "preferred_release_year": interaction["preferred_release_year"],
                "favorite_directors": interaction["favorite_directors"],
                "favorite_writers": interaction["favorite_writers"],
                "user_interaction_count": interaction["user_interaction_count"],
                "active_days": interaction["active_days"],
                "genres": movie["genres"],
                "rate": movie["rate"],
                "release_year": movie["release_date"].year,
                "runtime": movie["runtime"],
                "country": movie["country"],
                "is_series": movie["is_serie"],
                "adult": movie["adult"],
                "director_id": movie["director_id"],
                "writer_id": movie["writer_id"],
                "producer_id": movie["producer_id"],
                "popularity": movie["popularity"],
            }
            data.append(row)

        return data


def row_data(
        user_service: UserService = Depends(get_user_service),
        interaction_service: InteractionService = Depends(get_interaction_service),
        movie_service: MovieService = Depends(get_movie_service),
):
    return RowData(user_service, interaction_service, movie_service)
