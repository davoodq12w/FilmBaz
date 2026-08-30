from ..repositories.interaction import InteractionRepository, get_intraction_repository
from fastapi import Depends
from collections import Counter

from app.repositories.movie import (
    get_movie_repository,
    get_movie_relation_repository,
    MovieRelationRepository,
    MovieRepository
)


class InteractionService:
    def __init__(
            self, repo: InteractionRepository,
            movie_repo: MovieRepository,
            movie_relation_repo: MovieRelationRepository,
    ):
        self.repo = repo
        self.movie_repo = movie_repo
        self.movie_relation_repo = movie_relation_repo

    def padding_to_5(self, lst: list):
        return lst[:5] + [0] * max(0, 5 - len(lst))

    async def get_interactions(self, user_id: int):
        interactions = await self.repo.get_user_interactions(user_id)
        user_interaction_count = len(interactions)
        avg_interaction_weight = sum([i["weight"] for i in interactions]) / user_interaction_count
        active_days = (interactions[-1]["timestamp"] - interactions[0]["timestamp"]).days

        interactions_for_fov_movies = [i for i in interactions
                                       if i["interaction_type"] in [
                                           "save", "like", "share", "complete"
                                       ]]
        fov_movies_ids = [i["movie_id"] for i in interactions_for_fov_movies]
        fov_movies = await self.movie_repo.get_movies_basic(fov_movies_ids)

        fov_movie_runtimes = [m["runtime"] for m in fov_movies]
        preferred_runtime = sum(fov_movie_runtimes) / len(fov_movie_runtimes)

        fov_movie_releases = [m["release_date"].year for m in fov_movies]
        preferred_release_year = sum(fov_movie_releases) / len(fov_movie_releases)

        all_fov_directors = []
        all_fov_writers = []
        for movie_id in fov_movies_ids:
            result = await self.movie_relation_repo.get_movie_director_writer_producer(movie_id)
            all_fov_directors.append(result["director_id"])
            all_fov_writers.append(result["writer_id"])

        favorite_directors = [i for i, _ in Counter(all_fov_directors).most_common(5)]
        favorite_writers = [i for i, _ in Counter(all_fov_writers).most_common(5)]

        favorite_directors = self.padding_to_5(favorite_directors)
        favorite_writers = self.padding_to_5(favorite_writers)

        total_views = 0
        total_likes = 0
        total_saves = 0
        total_shares = 0
        total_comments = 0
        total_searches = 0
        total_watches = 0
        total_completes = 0

        for interaction in interactions:
            if interaction["interaction_type"] == "view":
                total_views += 1
            elif interaction["interaction_type"] == "like":
                total_likes += 1
            elif interaction["interaction_type"] == "save":
                total_saves += 1
            elif interaction["interaction_type"] == "share":
                total_shares += 1
            elif interaction["interaction_type"] == "comment":
                total_comments += 1
            elif interaction["interaction_type"] == "search":
                total_searches += 1
            elif interaction["interaction_type"] == "watch":
                total_watches += 1
            elif interaction["interaction_type"] == "complete":
                total_completes += 1
            else:
                pass

        data = {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_saves": total_saves,
            "total_shares": total_shares,
            "total_comments": total_comments,
            "total_searches": total_searches,
            "total_watches": total_watches,
            "total_completes": total_completes,
            "avg_interaction_weight": avg_interaction_weight,
            "active_days": active_days,
            "user_interaction_count": user_interaction_count,
            "preferred_runtime": preferred_runtime,
            "preferred_release_year": preferred_release_year,
            "favorite_directors": favorite_directors,
            "favorite_writers": favorite_writers,
        }
        return data


def get_interaction_service(
        repo: InteractionRepository = Depends(get_intraction_repository),
        movie_repo: MovieRepository = Depends(get_movie_repository),
        rels_repo: MovieRelationRepository = Depends(get_movie_relation_repository),
):
    return InteractionService(repo=repo, movie_repo=movie_repo, movie_relation_repo=rels_repo)
