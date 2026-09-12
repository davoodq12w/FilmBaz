import hashlib
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from account.models import UserRecommendation
from api_template import FilmBazAPI
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from film.models import (
    Movie,
    Genre,
)
from film.api.serializers import (
    MovieSerializer,
    OutPutHomePageSerializer,
    MovieListSerializer,
)
from django.db.models import Case, When, FloatField, Value
from django.core.cache import cache


class HomePageApi(FilmBazAPI):
    permission_classes = []

    @extend_schema(
        description="گرفتن دیتاهای صفحه خانه",
        responses={200: OutPutHomePageSerializer}
    )
    def get(self, request: Request, *args, **kwargs):

        if request.user.is_authenticated:
            favorite_genres = request.user.favorite_genres.all()
            if not favorite_genres.exists():
                by_chosen_genres = []
            else:
                by_chosen_genres_objs = Movie.objects.filter(genre__in=favorite_genres).distinct().order_by('-rate')[:7]
                by_chosen_genres = MovieSerializer(by_chosen_genres_objs, many=True).data

            rec_obj = UserRecommendation.objects.filter(user_id=request.user.id).first()
            if not rec_obj:
                recommendations = []

            else:
                recommendations_data = rec_obj.recommendations
                rec_movie_ids = [item["movie_id"] for item in recommendations_data]

                score_case = Case(
                    *[
                        When(
                            id=item["movie_id"],
                            then=Value(item["score"])
                        )
                        for item in recommendations_data
                    ],
                    output_field=FloatField()
                )
                recommendation_movies_data = (
                    Movie.objects
                    .filter(id__in=rec_movie_ids)
                    .annotate(score=score_case)
                    .order_by("-score")
                )[:7]
                recommendations = MovieSerializer(recommendation_movies_data).data

        else:
            by_chosen_genres = []
            recommendations = []

        new_movie_dats = Movie.objects.order_by('-release_date')[:7]
        top_movie_objs = Movie.objects.order_by('-rate')[:7]
        top_movies = MovieSerializer(top_movie_objs, many=True).data
        new_movies = MovieSerializer(new_movie_dats, many=True).data
        context = {
            "new_movies": new_movies,
            "top_movies": top_movies,
            "by_chosen_genres": by_chosen_genres,
            "recommendations": recommendations,
        }
        return Response(data=context, status=status.HTTP_200_OK)


class MovieListApi(FilmBazAPI):
    permission_classes = []
    filter_fields = ['genre_id', 'adult', 'release_date']
    ordering_fields = ['release_date', 'rate']
    cache_timeout = 60 * 15  # 15 minutes
    paginate_by = 21
    min_paginate_by = 7
    max_paginate_by = 21

    def _get_cache_key(self, request: Request):

        params = []

        for key, values in request.query_params.lists():
            for value in values:
                params.append((key, value))

        params = sorted(params)

        raw_key = str(params).encode("utf-8")
        hashed_key = hashlib.sha256(raw_key).hexdigest()

        return f"movies_list_{hashed_key}"

    def _get_filters(self, request: Request):
        filters = {}

        for field in self.filter_fields:
            value = request.query_params.get(field)

            if value in [None, ""]:
                continue

            if field == "adult":
                value = value.lower()

                if value == "true":
                    filters["adult"] = True
                elif value == "false":
                    filters["adult"] = False

            elif field == "genre_id":
                try:
                    filters["genres__id"] = int(value)

                except ValueError:
                    continue

            elif field == "release_date":
                try:
                    filters["release_date__year"] = int(value)
                except ValueError:
                    continue
        return filters

    def _get_ordering(self, request: Request):
        ordering = request.query_params.get("ordering")

        if ordering and ordering.lstrip("-") in self.ordering_fields:
            return ordering

        return None

    def _get_extra_context(self, request: Request):
        adult = request.query_params.get("adult", None)
        genre_id = request.query_params.get("genre_id", None)
        release_date = request.query_params.get("release_date", None)
        ordering = request.query_params.get("ordering", None)

        genre = Genre.objects.filter(id=genre_id).first()
        if not genre:
            genre = None,

        return {
            "selected_genre": genre,
            "selected_adult": adult,
            "selected_release_date": release_date,
            "selected_ordering": ordering,
            "page_size_param": request.query_params.get("page_size", self.paginate_by),
        }

    def _get_page_size(self, request: Request):
        try:
            page_size = int(request.query_params.get("page_size", self.max_paginate_by))
        except ValueError:
            page_size = self.paginate_by

        return max(self.min_paginate_by, min(page_size, self.max_paginate_by))

    def _paginated_movies(self, request: Request, movies: list[Movie]):
        page_size = self._get_page_size(request)
        page_number = request.query_params.get("page", 1)

        paginator = Paginator(movies, page_size)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return page_obj, paginator, page_size

    @extend_schema(
        description="گرفتن لیست فیلم ها",
        responses={200: MovieListSerializer},
        parameters=[
            OpenApiParameter(
                name='genre_id',
                type=int,
                enum=[i for i in range(1, 20)],
                required=False,
                examples=[
                    OpenApiExample(
                        name="مثال برای ژانر",
                        value=8
                    ),
                ]
            ),
            OpenApiParameter(
                name='adult',
                type=str,
                enum=["false", "true"],
                allow_blank=True,
                examples=[
                    OpenApiExample(
                        name="مثال برای رده بندی سنی",
                        value="false"
                    ),
                ]
            ),
            OpenApiParameter(
                name='release_date',
                type=int,
                required=False,
                examples=[
                    OpenApiExample(
                        name="مثال برای سال انتشار",
                        value=2014
                    ),
                ]
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                enum=['release_date', 'rate', '-release_date', '-rate'],
                allow_blank=True,
                examples=[
                    OpenApiExample(
                        name="مثال برای مرتب سازی",
                        value="-release_date"
                    ),
                ]
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                enum=[i for i in range(7, 22)],
                default=7,
                required=False,
                examples=[
                    OpenApiExample(
                        name="مثال برای صفحه بندی",
                        value=10
                    ),
                ]
            ),
        ]
    )
    def get(self, request: Request, *args, **kwargs):
        cache_key = self._get_cache_key(request)
        cache_marker = object()
        cached_movies = cache.get(cache_key, cache_marker)

        if cached_movies is not cache_marker:
            page_obj, paginator, page_size = self._paginated_movies(request, cached_movies)
            context = {
                "movies": page_obj.object_list,
                "page": page_obj.number,
                "num_pages": paginator.num_pages,
                "count": paginator.count,
                "page_size": page_size,
            }
            context.update(self._get_extra_context(request))
            serializer = MovieListSerializer(context)

            return Response(serializer.data, status=status.HTTP_200_OK)

        movies = Movie.objects.all()

        filters = self._get_filters(request)
        if filters:
            movies = movies.filter(**filters)

        ordering = self._get_ordering(request)
        if ordering:
            movies = movies.order_by(ordering)

        page_obj, paginator, page_size = self._paginated_movies(request, list(movies))

        cache.set(cache_key, list(movies), timeout=self.cache_timeout)

        context = {
            "movies": page_obj.object_list,
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "count": paginator.count,
            "page_size": page_size,
        }
        context.update(self._get_extra_context(request))
        serializer = MovieListSerializer(context)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GenresListApi(FilmBazAPI):
    ...


class YearsListApi(FilmBazAPI):
    ...
