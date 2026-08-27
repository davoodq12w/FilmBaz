import pandas as pd
from django.utils import timezone
from .models import Interaction
from film.models import Movie
from account.models import FilmBazUser
from people.models import MovieCrew
from collections import Counter


class DatasetBuilder:

    def padding_to_5(self, lst: list):
        return lst[:5] + [0] * max(0, 5 - len(lst))

    def get_movie_crews(self, movie):
        director_id = None
        writer_id = None
        producer_id = None

        for crew in movie.movie_crews.all():
            if crew.role == MovieCrew.CrewRole.DIRECTOR:
                director_id = crew.crew_id
            elif crew.role == MovieCrew.CrewRole.WRITER:
                writer_id = crew.crew_id
            elif crew.role == MovieCrew.CrewRole.PRODUCER:
                producer_id = crew.crew_id

        return director_id, writer_id, producer_id

    def build_users_df(self):
        users_df = []
        users = FilmBazUser.objects.prefetch_related(
            "favorite_genres",
            "interactions__movie",
            "interactions__movie__genres",
            "interactions__movie__movie_crews",
        )
        now = timezone.now()

        for user in users:
            interactions = list(user.interactions.all())
            interaction_count = len(interactions)
            last_interaction = user.interactions.all().order_by('-timestamp').first()
            first_interaction = user.interactions.all().order_by('timestamp').first()

            favorite_movies = {
                i.movie
                for i in interactions
                if i.movie and i.interaction_type in {
                    Interaction.Type.SAVE,
                    Interaction.Type.LIKE,
                    Interaction.Type.SHARE,
                    Interaction.Type.COMPLETE,
                }
            }
            movies_with_release = [m for m in favorite_movies if m.release_date]
            all_favorite_directors = []
            all_favorite_writers = []
            for i in interactions:
                director_id, writer_id, _ = self.get_movie_crews(i.movie)
                if director_id:
                    all_favorite_directors.append(director_id)
                if writer_id:
                    all_favorite_writers.append(writer_id)
            favorite_directors = [i for i, _ in Counter(all_favorite_directors).most_common(5)]
            favorite_writers = [i for i, _ in Counter(all_favorite_writers).most_common(5)]
            favorite_genres = [g.id for g in user.favorite_genres.all()]

            favorite_directors = self.padding_to_5(favorite_directors)
            favorite_writers = self.padding_to_5(favorite_writers)
            favorite_genres = self.padding_to_5(favorite_genres)

            users_df.append({
                "user_id": user.id,
                "account_age_days": (now - user.created).days,
                "total_views": sum(i.interaction_type == Interaction.Type.VIEW for i in interactions),
                "total_likes": sum(i.interaction_type == Interaction.Type.LIKE for i in interactions),
                "total_saves": sum(i.interaction_type == Interaction.Type.SAVE for i in interactions),
                "total_shares": sum(i.interaction_type == Interaction.Type.SHARE for i in interactions),
                "total_comments": sum(i.interaction_type == Interaction.Type.COMMENT for i in interactions),
                "total_searches": sum(i.interaction_type == Interaction.Type.SEARCH for i in interactions),
                "total_watches": sum(i.interaction_type == Interaction.Type.WATCH for i in interactions),
                "total_completes": sum(i.interaction_type == Interaction.Type.COMPLETE for i in interactions),
                "avg_interaction_weight": (
                    sum(i.weight for i in interactions) / interaction_count
                    if interaction_count else 0
                ),
                "favorite_genres": favorite_genres,
                "preferred_runtime": (
                    sum(m.runtime or 0 for m in favorite_movies)
                    / len(favorite_movies)
                    if favorite_movies else 0
                ),
                "preferred_release_year": (
                    sum(m.release_date.year for m in movies_with_release)
                    / len(movies_with_release)
                    if movies_with_release else 0
                ),
                "favorite_directors": list(favorite_directors),
                "favorite_writers": list(favorite_writers),
                "user_interaction_count": len(interactions),
                "active_days": (
                    (last_interaction.timestamp - first_interaction.timestamp).days
                    if last_interaction and first_interaction
                    else 0
                ),
            })

        df = pd.DataFrame(users_df)
        df = df.convert_dtypes()
        return df[[
            "user_id",
            "account_age_days",
            "total_views",
            "total_likes",
            "total_saves",
            "total_shares",
            "total_comments",
            "total_searches",
            "total_watches",
            "total_completes",
            "avg_interaction_weight",
            "favorite_genres",
            "preferred_runtime",
            "preferred_release_year",
            "favorite_directors",
            "favorite_writers",
            "user_interaction_count",
            "active_days",
        ]]

    def build_movies_df(self):
        movies_df = []
        movies = Movie.objects.prefetch_related(
            "genres",
            "interactions",
            "movie_crews",
        )

        for movie in movies:
            director_id, writer_id, producer_id = self.get_movie_crews(movie)
            genres = [g.id for g in movie.genres.all()]
            genres = self.padding_to_5(genres)
            movies_df.append({
                "movie_id": movie.id,
                "genres": genres,
                "rate": float(movie.rate),
                "release_year": (
                    movie.release_date.year
                    if movie.release_date
                    else None
                ),
                "runtime": movie.runtime,
                "country": movie.country,
                "is_series": movie.is_serie,
                "adult": movie.adult,
                "director_id": director_id,
                "writer_id": writer_id,
                "producer_id": producer_id,
                "popularity": len(movie.interactions.all()),
            })
        df = pd.DataFrame(movies_df)
        df = df.convert_dtypes()
        return df[[
            "movie_id",
            "genres",
            "rate",
            "release_year",
            "runtime",
            "country",
            "is_series",
            "adult",
            "director_id",
            "writer_id",
            "producer_id",
            "popularity",
        ]]

    def build_interactions_df(self):

        interactions = (
            Interaction.objects
            .select_related("user", "movie")
            .order_by("user_id", "movie_id")
        )

        grouped = {}

        for interaction in interactions:
            key = (interaction.user_id, interaction.movie_id)

            if key not in grouped:
                grouped[key] = {
                    "user_id": interaction.user_id,
                    "movie_id": interaction.movie_id,
                    "target_score": 0,
                }

            row = grouped[key]

            row["target_score"] += interaction.weight

        df = pd.DataFrame(grouped.values())
        df = df.convert_dtypes()

        return df[[
            "user_id",
            "movie_id",
            "target_score",
        ]]

    def build(self):
        users = self.build_users_df()
        movies = self.build_movies_df()
        interactions = self.build_interactions_df()

        return (
            interactions
            .merge(users, on="user_id")
            .merge(movies, on="movie_id")
        )
