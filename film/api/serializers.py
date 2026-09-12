from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from film.models import Genre, Movie
from people.api.serializers import CastSerializer, MovieCrewSerializer


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "en_name", "fa_name", "slug"]
        read_only_fields = ["id", "en_name", "fa_name", "slug"]


class MovieSerializer(serializers.ModelSerializer):
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


class OutPutHomePageSerializer(serializers.Serializer):
    new_movies = MovieSerializer(many=True)
    top_movies = MovieSerializer(many=True)
    by_chosen_genres = MovieSerializer(many=True)
    recommendations = MovieSerializer(many=True)


class MovieListSerializer(serializers.Serializer):
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
