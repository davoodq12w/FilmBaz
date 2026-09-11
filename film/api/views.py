from account.models import UserRecommendation
from api_template import FilmBazAPI
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_spectacular.utils import extend_schema
from film.models import Movie
from film.api.serializers import (
    MovieSerializer,
    HomePageSerializer,
)
from django.db.models import Case, When, FloatField, Value


class HomePageApi(FilmBazAPI):
    permission_classes = []

    @extend_schema(
        description="گرفتن دیتاهای صفحه خانه",
        responses={200: HomePageSerializer}
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
