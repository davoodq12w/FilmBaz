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
    Comment,
    MovieEpisode,
    WatchProgress,
)
from film.api.serializers import (
    MovieSerializer,
    HomePageOutputSerializer,
    MovieListSerializer,
    GenreSerializer,
    YearSerializer,
    MovieDetailSerializer,
    AddCommentSerializer,
    SearchSerializer,
    SaveLikeSerializer,
    SaveOutputSerializer,
    LikeOutputSerializer,
    WatchMovieSerializer,
    WatchProgressInputSerializer,
    CostomListMovieSerializer,
)
from django.db.models import Case, When, FloatField, Value
from django.core.cache import cache
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.permissions import AllowAny


class HomePageApi(FilmBazAPI):
    """
    Api used for giving some movies that have a high chance of being watched.
    all users access to the aview
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        description="گرفتن دیتاهای صفحه خانه . "
                    "اگر لیست ژانر های مورد علاقه خالی بود بهتر است یوزر ابتدا ژانرهای مورد علاقه اش را انتخال کند",
        responses={200: HomePageOutputSerializer},
    )
    def get(self, request: Request, *args, **kwargs):
        """
        method giving 4 list of different topic. every topic contain 7 movie.
        if user not authenticated lists are 2.
        """
        if request.user.is_authenticated:
            # getting movies by user favorite genres and orders by rating of movies.
            favorite_genres = request.user.favorite_genres.all()
            if not favorite_genres.exists():
                by_chosen_genres = []
            else:
                by_chosen_genres_objs = Movie.objects.filter(genre__in=favorite_genres).distinct().order_by('-rate')[:7]
                by_chosen_genres = MovieSerializer(by_chosen_genres_objs, many=True).data

            # getting recommended movies to user and order by which is most relevant to the user interests.
            rec_obj = UserRecommendation.objects.filter(user_id=request.user.id).first()
            if not rec_obj:
                recommendations = []

            else:
                recommendations_data = rec_obj.recommendations
                rec_movie_ids = [item["movie_id"] for item in recommendations_data]

                # create a custom field for ordering movies by score.
                score_case = Case(
                    *[
                        When(
                            id=item["movie_id"],
                            then=Value(item["score"])
                        )
                        for item in recommendations_data
                    ],
                    output_field=FloatField()
                )  # giving every id a score in django models field then used the score for ordering.
                recommendation_movies_data = (
                    Movie.objects
                    .filter(id__in=rec_movie_ids)
                    .annotate(score=score_case)  # set the field to objects.
                    .order_by("-score")  # sort by score.
                )[:7]
                recommendations = MovieSerializer(recommendation_movies_data).data

        else:
            by_chosen_genres = []
            recommendations = []

        new_movie_dats = Movie.objects.order_by('-release_date')[:7]
        top_movie_objs = Movie.objects.order_by('-rate')[:7]
        top_movies = MovieSerializer(top_movie_objs, many=True).data
        new_movies = MovieSerializer(new_movie_dats, many=True).data

        # all lists are serialized so we do not need to use HomePageOutputSerializer for respose.
        context = {
            "new_movies": new_movies,
            "top_movies": top_movies,
            "by_chosen_genres": by_chosen_genres,
            "recommendations": recommendations,
        }
        return Response(data=context, status=status.HTTP_200_OK)


class ByUserGenresMoviesApi(FilmBazAPI):
    """
    Api used for givig paginated movies that filters by user favorite genres.
    only authenticated users access to the view.
    """
    ordering_fields = ['release_date', 'rate']
    paginate_by = 21
    min_paginate_by = 7
    max_paginate_by = 21

    def _get_ordering(self, request: Request):
        """
        inner method giving orderings for queryset if there was valid ordering fields in request.
        """
        ordering = request.query_params.get("ordering")

        if ordering and ordering.lstrip("-") in self.ordering_fields:
            return ordering

        return None

    def _get_page_size(self, request: Request):
        """
        inner method giving custom page size if its in valid range else returned default value.
        """
        try:
            page_size = int(request.query_params.get("page_size", self.max_paginate_by))
        except ValueError:
            page_size = self.paginate_by

        return max(self.min_paginate_by, min(page_size, self.max_paginate_by))

    def _paginated_movies(self, request: Request, movies: list[Movie]):
        """
        inner method giving query set of movies in requested page & paginator object & page size.
        if page number value is not valid its returned page 1.
        if page number out of range its returned last page.
        """
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
        description="گرفتن لیست فیلم ها طبق ژانر ها منتخب کاربر",
        responses={200: CostomListMovieSerializer},
        parameters=[
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
        """
        method giving paginated data of movies that filters by user favorite genres.
        """
        favorite_genres = request.user.favorite_genres.all()
        if not favorite_genres.exists():
            return Response({"Warning": "User not choose there favorite genres."}, status=status.HTTP_204_NO_CONTENT)

        movies = Movie.objects.filter(genre__in=favorite_genres).distinct()

        # if there was any valid ordering its applied
        ordering = self._get_ordering(request)
        if ordering:
            movies = movies.order_by(ordering)

        page_obj, paginator, page_size = self._paginated_movies(request, list(movies))
        ordering = request.query_params.get("ordering", None)

        context = {
            "movies": page_obj.object_list,
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "count": paginator.count,
            "page_size": page_size,
            "selected_ordering": ordering,
            "page_size_param": request.query_params.get("page_size", self.paginate_by),
        }
        # useing serializer for serializing the data and better data returning.
        serializer = CostomListMovieSerializer(context)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecommendationsMoviesApi(FilmBazAPI):
    """
    Api used for givig paginated movies that recommended to used by ml model.
    only authenticated users access to the view.
    """
    ordering_fields = ['release_date', 'rate']
    paginate_by = 21
    min_paginate_by = 7
    max_paginate_by = 21

    def _get_ordering(self, request: Request):
        """
        inner method giving orderings for queryset if there was valid ordering fields in request.
        """
        ordering = request.query_params.get("ordering")

        if ordering and ordering.lstrip("-") in self.ordering_fields:
            return ordering

        return None

    def _get_page_size(self, request: Request):
        """
        inner method giving custom page size if its in valid range else returned default value.
        """
        try:
            page_size = int(request.query_params.get("page_size", self.max_paginate_by))
        except ValueError:
            page_size = self.paginate_by

        return max(self.min_paginate_by, min(page_size, self.max_paginate_by))

    def _paginated_movies(self, request: Request, movies: list[Movie]):
        """
        inner method giving query set of movies in requested page & paginator object & page size.
        if page number value is not valid its returned page 1.
        if page number out of range its returned last page.
        """
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
        description="گرفتن لیست فیلم های پیشنهاد شده به کاربر",
        responses={200: CostomListMovieSerializer},
        parameters=[
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
        """
        method giving paginated data of movies that recommended to used by ml model.
        """
        rec_obj = UserRecommendation.objects.filter(user_id=request.user.id).first()
        if not rec_obj:
            return Response({"Warning": "User not any recommendations yet."}, status=status.HTTP_204_NO_CONTENT)

        recommendations_data = rec_obj.recommendations
        rec_movie_ids = [item["movie_id"] for item in recommendations_data]

        # create a custom field for ordering movies by score.
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
        # giving every id a score in django models field then used the score for ordering.
        movies = (
            Movie.objects
            .filter(id__in=rec_movie_ids)
            .annotate(score=score_case)  # set the field to objects.
            .order_by("-score")  # sort by score.
        )

        # if there was any valid ordering its applied
        ordering = self._get_ordering(request)
        if ordering:
            movies = movies.order_by(ordering)

        page_obj, paginator, page_size = self._paginated_movies(request, list(movies))
        ordering = request.query_params.get("ordering", None)

        context = {
            "movies": page_obj.object_list,
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "count": paginator.count,
            "page_size": page_size,
            "selected_ordering": ordering,
            "page_size_param": request.query_params.get("page_size", self.paginate_by),
        }
        # useing serializer for serializing the data and better data returning.
        serializer = CostomListMovieSerializer(context)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieListApi(FilmBazAPI):
    """
    Api used for givig paginated movies.
    Performs filtering and ordering and caching data.
    all users access to the view.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    filter_fields = ['genre_id', 'adult', 'release_date']
    ordering_fields = ['release_date', 'rate']
    cache_timeout = 60 * 15  # 15 minutes
    paginate_by = 21
    min_paginate_by = 7
    max_paginate_by = 21

    def _get_cache_key(self, request: Request):
        """
        inner method used for creating cache key with data of request.
        performs cache data for same filtering and ordering and pagination.
        """

        params = []

        for key, values in request.query_params.lists():
            for value in values:
                params.append((key, value))

        # sorting valus allow us to leser cashing data if parameters in request are givin not in same order.
        params = sorted(params)

        raw_key = str(params).encode("utf-8")
        hashed_key = hashlib.sha256(raw_key).hexdigest()

        return f"movies_list_{hashed_key}"

    def _get_filters(self, request: Request):
        """
        inner method giving filters for queryset if there were valid filters.
        """
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
        """
        inner method giving orderings for queryset if there was valid ordering fields in request.
        """
        ordering = request.query_params.get("ordering")

        if ordering and ordering.lstrip("-") in self.ordering_fields:
            return ordering

        return None

    def _get_extra_context(self, request: Request):
        """
        inner method giving data about applied filters or orderings or paginations.
        """
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
        """
        inner method giving custom page size if its in valid range else returned default value.
        """
        try:
            page_size = int(request.query_params.get("page_size", self.max_paginate_by))
        except ValueError:
            page_size = self.paginate_by

        return max(self.min_paginate_by, min(page_size, self.max_paginate_by))

    def _paginated_movies(self, request: Request, movies: list[Movie]):
        """
        inner method giving query set of movies in requested page & paginator object & page size.
        if page number value is not valid its returned page 1.
        if page number out of range its returned last page.
        """
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
        """
        method giving a cached or uncached queryset of movies that applied orderings, filterings and pagintions on them.
        """
        cache_key = self._get_cache_key(request)

        # if ther was no cache for the key cache.get return object becuose we set it for get method.
        # so we use object function for that is response of get cache is an empty object or
        # is an empty queryset value for the combonations of request parameters.
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

        # if there were valid filters then applied.
        filters = self._get_filters(request)
        if filters:
            movies = movies.filter(**filters)

        # if there was valid ordering then applied.
        ordering = self._get_ordering(request)
        if ordering:
            movies = movies.order_by(ordering)

        page_obj, paginator, page_size = self._paginated_movies(request, list(movies))

        # set cache for same combonations of parameters in other requests.
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


class GenreListApi(FilmBazAPI):
    """
    Api used for giving all genres in DataBase.
    all users access to the view.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        description="گرفتن تمامی ژانرها",
        responses={200: GenreSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        """
        method used for giving queryset of genres
        """
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class YearListApi(FilmBazAPI):
    """
    Api used for giving all years of when movies created in DataBase.
    all users access to the view.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        description="گرفتن تمامی سال های ساخت فیلم ها",
        responses={200: YearSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        """
        method giving a list of years of movies.
        """
        years = [
            date_obj.year
            for date_obj in Movie.objects.filter(release_date__isnull=False).dates('release_date', 'year')
        ]

        serializer = YearSerializer(years, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieDetailApi(FilmBazAPI):
    """
    Api used for giving the full details of movie.
    only authenticated users can access the view.
    """

    @extend_schema(
        description="گرفتن اطلاعات کامل یک فیلم",
        responses={200: MovieDetailSerializer},
    )
    def get(self, request: Request, pk=None, slug=None, *args, **kwargs):
        """
        method datas of movie.
        take id & slug of one movie and giving all data of that movie.
        """
        if pk is None or slug is None:
            return Response({"Error": "pk and slug most be given."}, status=status.HTTP_400_BAD_REQUEST)

        # creat cache keys
        comments_cache_key = f"movie_comments_{pk}_{slug}"
        episodes_cache_key = f"movie_episodes_{pk}_{slug}"
        context = {}

        try:
            # get cached comments
            cache_marker = object()
            cached_comments = cache.get(comments_cache_key, cache_marker)
            movie = Movie.objects.filter(id=pk, slug=slug).first()
            if movie is None:
                return Response({"Error": "movie with this data is not exsits."}, status=status.HTTP_404_NOT_FOUND)
            context["movie"] = movie

            if cached_comments is not cache_marker:
                context["comments"] = cached_comments
            else:
                comments = Comment.objects.filter(movie__id=pk, movie__slug=slug)
                context["comments"] = comments
                cache.set(comments_cache_key, comments)

            # get cached episodes
            cached_episodes = cache.get(episodes_cache_key, cache_marker)
            if cached_episodes is not cache_marker:
                context["episodes"] = cached_episodes
            else:
                episodes = MovieEpisode.objects.filter(movie__id=pk, movie__slug=slug).order_by("season", "episode")
                context["episodes"] = episodes
                cache.set(episodes_cache_key, episodes)

            # add trailer in context
            if movie.trailer is not None:
                context["trailer"] = movie.trailer
            else:
                context["trailer"] = None

            # get last completed episode
            last_watch = WatchProgress.objects.filter(
                episode__movie__slug=slug,
                episode__movie__id=pk,
                user=request.user,
                completed=True,
            ).order_by("-episode__season", "-episode__episode").first()

            # get next episode to watch.
            if last_watch is not None:
                unwatched_episode = last_watch.episode.get_next_episode()
            else:
                unwatched_episode = movie.episodes.filter(season=1, episode=1).first()

            context["unwatched_episode"] = unwatched_episode
            context["last_watch"] = last_watch
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = MovieDetailSerializer(context)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddCommentApi(FilmBazAPI):
    """
    Api used for adding comments.
    only authenticated usese access to the view.
    """

    @extend_schema(
        description="اضافه کردن نظر برای یک فیلم توسط کاربر",
        request=AddCommentSerializer,
        responses={201: AddCommentSerializer},
        examples=[
            OpenApiExample(
                name="دیتای لازم",
                value={
                    "movie_id": 2745,
                    "text": "در بین فیلم های این ژانر این بهترین فیلم هستش."
                },
                request_only=True,
            )

        ]
    )
    def post(self, request: Request, *args, **kwargs):
        """
        method for add a comment bllow of a movie.
        take id of movie and text of comment and creating new comment for movie.
        """
        serializer = AddCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movie_id = serializer.validated_data["movie_id"]
        movie = Movie.objects.filter(id=movie_id).first()
        if movie is None:
            return Response({"Error": "movie with this data is not exsits."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "movie": movie,
            "text": serializer.validated_data["text"],
            "user": request.user,
        }
        comment = Comment.objects.create(**data)
        result = AddCommentSerializer(comment).data
        return Response(result, status=status.HTTP_201_CREATED)


class SearchApi(FilmBazAPI):
    """
    Api used for searching movies.
    all users access to the view.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def _get_results(self, query):
        """
        inner method giving all results of searching movies.
        search by orginal and persion title of movies.
        """
        try:
            result1 = Movie.objects.annotate(
                similarity=TrigramSimilarity("fa_title", query)).filter(similarity__gt=0.1)
            result2 = Movie.objects.annotate(
                similarity=TrigramSimilarity("orj_title", query)).filter(similarity__gt=0.1)

            # merging all results and make sure to not existing any dublicate movie object
            movie_result = (result1 | result2).order_by("-similarity")
        except Exception as e:
            raise ValueError(f"error: {e}")
        return movie_result

    @extend_schema(
        description="گرفتن لیستی از فیلم ها بر اساس متن ارسالی",
        request=SearchSerializer,
        responses={200: MovieSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="متن سرچ شده انگلیسی",
                value={
                    "query": "The Shawshank Redemption"
                },
                request_only=True,
            ),
            OpenApiExample(
                name="متن سرچ شده فارسی",
                value={
                    "query": "رستگاری در شاوشنگ"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request: Request, *args, **kwargs):
        """
        method giving all matched movies with query of search.
        """
        serializer = SearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        movies = self._get_results(query)

        movie_serializer = MovieSerializer(movies, many=True)
        return Response(movie_serializer.data, status=status.HTTP_200_OK)


class SaveMovieApi(FilmBazAPI):
    """
    Api used for adding and removing movie to user saves list.
    only authenticated usese access to the view.
    """

    @extend_schema(
        description="ذخیره کردن فیلم ها برای تماشای بعدا",
        request=SaveLikeSerializer,
        responses={200: SaveOutputSerializer},
        examples=[
            OpenApiExample(
                name="داده های لازم",
                value={
                    "pk": 2345,
                    "slug": "persion_lessense"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request: Request, *args, **kwargs):
        """
        method add or remove the movie to user saves list.
        take id and slug of movie and add or remove movie of the list.
        """
        serializer = SaveLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pk = serializer.validated_data["pk"]
        slug = serializer.validated_data["slug"]

        movie = Movie.objects.filter(id=pk, slug=slug).first()
        if movie is None:
            return Response({"Error": "movie with this data is not exsits."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if movie in user.saves.all():
            user.saves.remove(movie)
            is_save = False

        else:
            user.saves.add(movie)
            is_save = True

        data = {"is_save": is_save}
        out_seriazier = SaveOutputSerializer(data)

        return Response(out_seriazier.data, status=status.HTTP_200_OK)


class LikeMovieApi(FilmBazAPI):
    """
    Api used for adding and removing movie to user saves list.
    only authenticated usese access to the view.
    """

    @extend_schema(
        description="لایک کردن فیلم ها",
        request=SaveLikeSerializer,
        responses={200: LikeOutputSerializer},
        examples=[
            OpenApiExample(
                name="داده های لازم",
                value={
                    "pk": 2345,
                    "slug": "persion_lessense"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request: Request, *args, **kwargs):
        """
        method add or remove the movie to user likes list.
        take id and slug of movie and add or remove movie of the list.
        """
        serializer = SaveLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pk = serializer.validated_data["pk"]
        slug = serializer.validated_data["slug"]

        movie = Movie.objects.filter(id=pk, slug=slug).first()
        if movie is None:
            return Response({"Error": "movie with this data is not exsits."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if movie in user.likes.all():
            user.saves.remove(movie)
            is_like = False

        else:
            user.likes.add(movie)
            is_like = True

        data = {"is_like": is_like}
        out_seriazier = LikeOutputSerializer(data)

        return Response(out_seriazier.data, status=status.HTTP_200_OK)


class WatchMovieApi(FilmBazAPI):
    """
    Api used for giving all data about the one episode of movies.
    only authenticated usese access to the view.
    """

    @extend_schema(
        description="گرفتن اطلاعات مربوط به یک اپیزود از فیلم و سریال ها",
        responses={200: WatchMovieSerializer}
    )
    def get(self, request: Request, pk=None, *args, **kwargs):
        """
        method giving all data aboute episode.
        take id of episode object and giving full data of the episode.
        """
        if not pk:
            return Response({"Error": "movie episode id most be given"}, status=status.HTTP_400_BAD_REQUEST)

        episode = MovieEpisode.objects.filter(id=pk).first()

        if episode is None:
            return Response({"Error": "episode with this data is not exsits."}, status=status.HTTP_404_NOT_FOUND)

        # get watch progress object
        watch_progress = episode.watch_progress.filter(user=request.user).first()
        if watch_progress is not None:
            watch_position = watch_progress.position
        else:
            watch_position = 0

        # get next episode of selected episode
        if episode.movie.is_serie:
            next_episode = episode.get_next_episode()
        else:
            next_episode = None

        data = {
            "episode": episode,
            "watch_progress": watch_position,
            "next_episode": next_episode,
        }

        # using serializer for serializering response data.
        serializer = WatchMovieSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WatchProgressApi(FilmBazAPI):
    """
    Api used for updating watch progress of episode.
    only authenticated usese access to the view.
    """

    @extend_schema(
        description="اپدیت کردن مقدار پراگرس یوزر برای یک اپیزود",
        request=WatchProgressInputSerializer,
        responses={200: {"Success": "watchprogress updated."}},
        examples=[
            OpenApiExample(
                name="دادهای لازم",
                value={
                    "episode_id": 235,
                    "position": 780,
                    "completed": False,
                },
                request_only=True,
            )
        ]
    )
    def post(self, request: Request, *args, **kwargs):
        """
        method update details of watch progress object of episode.
        take episode id and progress data and update the obj.
        """
        input_serializer = WatchProgressInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        pk = input_serializer.validated_data["episode_id"]
        position = input_serializer.validated_data["position"]
        completed = input_serializer.validated_data["completed"]

        episode = MovieEpisode.objects.filter(id=pk).first()
        if episode is None:
            return Response({"Error": "episode with this data is not exsits."}, status=status.HTTP_404_NOT_FOUND)

        # if the object was exists it will be updated, or we create new objects for user
        WatchProgress.objects.update_or_create(
            user=request.user,
            episode=episode,
            defaults={
                "position": position,
                "completed": completed,
            }
        )
        return Response({"Success": "watchprogress updated."}, status=status.HTTP_200_OK)
