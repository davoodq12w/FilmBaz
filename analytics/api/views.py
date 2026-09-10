from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from analytics.api.serializers import ShareIntractionSerializer
from api_template import FilmBazAPI
from film.models import Movie
from analytics.models import Interaction


class ShareIntractionApi(FilmBazAPI):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="ساختن اینترکشن اشتراکگذاری برای کاربر",
        request=ShareIntractionSerializer,
        responses={200: "Success", 404: "Error", 403: "Forbidden", 400: "Bad Request"},
        examples=[OpenApiExample(
            name="دیتای لازم",
            value={
                "movie_id": 3245,
                "movie_slug": "IT"
            },
            request_only=True,
        )],
        tags=["interaction"],
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = ShareIntractionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movie_id = serializer.validated_data['movie_id']
        movie_slug = serializer.validated_data['movie_slug']

        try:
            movie = Movie.objects.get(pk=movie_id, movie_slug=movie_slug)

        except Movie.DoesNotExist:
            return Response({"Error": "movie with this data not exsits."}, status=status.HTTP_404_NOT_FOUND)

        Interaction.objects.get_or_create(
            user=request.user,
            movie=movie,
            interaction_type=Interaction.Type.SHARE,
            weight=1.2
        )
        return Response({"Success": "Interaction created successfully."}, status=status.HTTP_201_CREATED)
