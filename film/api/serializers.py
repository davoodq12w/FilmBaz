from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from film.models import Genre, Movie, Comment, WatchProgress, MovieEpisode, MovieTrailer
from people.api.serializers import CastSerializer, MovieCrewSerializer


class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for genre objects.
    """

    class Meta:
        model = Genre
        fields = ["id", "en_name", "fa_name", "slug"]
        read_only_fields = ["id", "en_name", "fa_name", "slug"]


class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for movie objects.
    """
    genres = serializers.SerializerMethodField()
    movie_crews = serializers.SerializerMethodField()
    casts = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "poster", "backdrop", "fa_title", "orj_title", "slug",
            "description", "rate", "release_date", "country",
            "runtime", "is_serie", "adult", "genres", "created",
            "movie_crews", "casts"
        ]

    @extend_schema_field(GenreSerializer(many=True))
    def get_genres(self, obj: Movie):
        genres = obj.genres.all()
        if genres:
            return GenreSerializer(genres, many=True).data
        return []

    @extend_schema_field(MovieCrewSerializer(many=True))
    def get_movie_crews(self, obj: Movie):
        crews = obj.movie_crews.all()
        if crews:
            return MovieCrewSerializer(crews, many=True).data
        return []

    @extend_schema_field(CastSerializer(many=True))
    def get_casts(self, obj: Movie):
        casts = obj.casts.all()
        if casts:
            return CastSerializer(casts, many=True).data
        return []


class HomePageOutputSerializer(serializers.Serializer):
    """
    Serializer used for serialzing homepage response.
    """
    new_movies = MovieSerializer(many=True)
    top_movies = MovieSerializer(many=True)
    by_chosen_genres = MovieSerializer(many=True)
    recommendations = MovieSerializer(many=True)


class CostomListMovieSerializer(serializers.Serializer):
    """
    Serializer used for serialzing response of ByUserGenresMoviesApi & RecommendationsMoviesApi.
    """
    selected_ordering = serializers.CharField()
    page_size_param = serializers.IntegerField()
    movies = MovieSerializer(many=True)
    page = serializers.IntegerField()
    num_pages = serializers.IntegerField()
    count = serializers.IntegerField()
    page_size = serializers.IntegerField()


class MovieListSerializer(serializers.Serializer):
    """
    Serializer used for serialzing response of MovieListApi.
    """
    selected_genre = GenreSerializer()
    selected_adult = serializers.BooleanField()
    selected_release_date = serializers.IntegerField()
    selected_ordering = serializers.CharField()
    page_size_param = serializers.IntegerField()
    movies = MovieSerializer(many=True)
    page = serializers.IntegerField()
    num_pages = serializers.IntegerField()
    count = serializers.IntegerField()
    page_size = serializers.IntegerField()


class YearSerializer(serializers.Serializer):
    """
    Serializer used for response of YearListApi.
    """
    year = serializers.IntegerField()


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer used for show comment detail.
    """

    class Meta:
        model = Comment
        fields = ["text", "created"]


class WatchProgressSerializer(serializers.ModelSerializer):
    """
    Serializer used for create and show watch progress detail.
    """

    class Meta:
        model = WatchProgress
        fields = ["episode", "position", "completed", "updated_at"]


class MovieTrailerSerializer(serializers.ModelSerializer):
    """
    Serializer for trailer objects.
    """

    class Meta:
        model = MovieTrailer
        fields = ["file", "created_at"]


class MovieEpisodeSerializer(serializers.ModelSerializer):
    """
    Serializer for movie episode objects.
    """

    class Meta:
        model = MovieEpisode
        fields = ["episode", "season", "file", "duration", "intro_start", "intro_end", "credits_start", "created_at"]


class MovieDetailSerializer(serializers.Serializer):
    """
    Serializer used for response of MovieDetailApi.
    """
    movie = MovieSerializer()
    trailer = MovieTrailerSerializer()
    episodes = MovieEpisodeSerializer(many=True)
    comments = CommentSerializer(many=True)
    unwatched_episode = MovieEpisodeSerializer()
    last_watch = WatchProgressSerializer()


class AddCommentSerializer(serializers.Serializer):
    """
    Serializer used for create comment detail.
    """

    movie_id = serializers.IntegerField(required=True)
    text = serializers.CharField(required=True)


class SearchSerializer(serializers.Serializer):
    """
    Serializer used for request of SearchApi.
    """
    query = serializers.CharField()


class SaveLikeSerializer(serializers.Serializer):
    """
    Serializer used for request of SaveMovieApi and LikeMovieApi.
    """
    slug = serializers.SlugField(required=True)
    pk = serializers.IntegerField(required=True)


class SaveOutputSerializer(serializers.Serializer):
    """
    Serializer used for response of SaveMovieApi.
    """
    is_save = serializers.BooleanField()


class LikeOutputSerializer(serializers.Serializer):
    """
    Serializer used for response of LikeMovieApi.
    """

    is_like = serializers.BooleanField()


class WatchMovieSerializer(serializers.Serializer):
    """
    Serializer used for response of WatchMovieApi.
    """
    episode = MovieEpisodeSerializer()
    watch_progress = WatchProgressSerializer()
    next_episode = MovieEpisodeSerializer()


class WatchProgressInputSerializer(serializers.Serializer):
    """
    Serializer used for request of WatchProgressApi.
    """
    episode_id = serializers.IntegerField(required=True)
    position = serializers.IntegerField(required=True, help_text="second")
    completed = serializers.BooleanField(required=True)
