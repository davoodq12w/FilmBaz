import pandas as pd
from django.utils import timezone
from .models import Interaction
from film.models import Movie
from account.models import FilmBazUser
from people.models import MovieCrew


class DatasetBuilder:

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
                }
            }
            movies_with_release = [m for m in favorite_movies if m.release_date]
            favorite_directors = set()
            favorite_writers = set()
            for movie in favorite_movies:
                director_id, writer_id, _ = self.get_movie_crews(movie)
                if director_id:
                    favorite_directors.add(director_id)
                if writer_id:
                    favorite_writers.add(writer_id)

            users_df.append({
                "user_id": user.id,
                "account_age_days": (now - user.created).days,
                "total_views": sum(i.interaction_type == Interaction.Type.VIEW for i in interactions),
                "total_likes": sum(i.interaction_type == Interaction.Type.LIKE for i in interactions),
                "total_saves": sum(i.interaction_type == Interaction.Type.SAVE for i in interactions),
                "total_shares": sum(i.interaction_type == Interaction.Type.SHARE for i in interactions),
                "total_comments": sum(i.interaction_type == Interaction.Type.COMMENT for i in interactions),
                "total_searches": sum(i.interaction_type == Interaction.Type.SEARCH for i in interactions),
                "avg_interaction_weight": (
                    sum(i.weight for i in interactions) / interaction_count
                    if interaction_count else 0
                ),
                "favorite_genres": [
                    g.en_name for g in user.favorite_genres.all()
                ],
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
                "interaction_count": len(interactions),
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
            "avg_interaction_weight",
            "favorite_genres",
            "preferred_runtime",
            "preferred_release_year",
            "favorite_directors",
            "favorite_writers",
            "interaction_count",
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
            movies_df.append({
                "movie_id": movie.id,
                "genres": [
                    g.en_name
                    for g in movie.genres.all()
                ],
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
        interactions_df = []

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
                    "view_count": 0,
                    "liked": False,
                    "saved": False,
                    "shared": False,
                    "comment_count": 0,
                    "search_count": 0,
                    "interaction_count": 0,
                    "target_score": 0,
                    "last_interaction": interaction.timestamp,
                }

            row = grouped[key]

            row["interaction_count"] += 1
            row["target_score"] += interaction.weight

            if interaction.timestamp > row["last_interaction"]:
                row["last_interaction"] = interaction.timestamp

            if interaction.interaction_type == Interaction.Type.VIEW:
                row["view_count"] += 1

            elif interaction.interaction_type == Interaction.Type.LIKE:
                row["liked"] = True

            elif interaction.interaction_type == Interaction.Type.SAVE:
                row["saved"] = True

            elif interaction.interaction_type == Interaction.Type.SHARE:
                row["shared"] = True

            elif interaction.interaction_type == Interaction.Type.COMMENT:
                row["comment_count"] += 1

            elif interaction.interaction_type == Interaction.Type.SEARCH:
                row["search_count"] += 1

        df = pd.DataFrame(grouped.values())
        df = df.convert_dtypes()

        return df[[
            "user_id",
            "movie_id",
            "view_count",
            "liked",
            "saved",
            "shared",
            "comment_count",
            "search_count",
            "interaction_count",
            "target_score",
            "last_interaction",
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
