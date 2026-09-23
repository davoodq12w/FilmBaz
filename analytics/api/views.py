from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from analytics.api.serializers import InteractionSerializer
from api_template import FilmBazAPI
from film.models import Movie
from analytics.models import Interaction


class IntractionApi(FilmBazAPI):
    """
    Api View user for creation of interactions
    only authenticated users access the API
    """

    @extend_schema(
        description="ساختن اینترکشن برای کاربر",
        request=InteractionSerializer,
        responses={200: "Success", 404: "Error", 403: "Forbidden", 400: "Bad Request"},
        examples=[OpenApiExample(
            name="دیتای لازم",
            value={
                "movie_id": 3245,
                "movie_slug": "IT",
                "interaction_type": "view",
            },
            request_only=True,
        )],
        tags=["interaction"],
    )
    def post(self, request: Request, *args, **kwargs):
        """
        create interactions
        take id & slug of movie and create interaction object for authenticated user.
        """
        serializer = InteractionSerializer(data=request.data)

        # if there was any validations error raise automaticlly
        serializer.is_valid(raise_exception=True)

        movie_id = serializer.validated_data['movie_id']
        movie_slug = serializer.validated_data['movie_slug']

        try:
            movie = Movie.objects.get(pk=movie_id, movie_slug=movie_slug)

        except Movie.DoesNotExist:
            return Response({"Error": "movie with this data not exsits."}, status=status.HTTP_404_NOT_FOUND)

        # enumerate of interactions weight for simpl usage.
        weights = {
            "view": 0.2,
            "like": 1.0,
            "save": 1.5,
            "comment": 0.5,
            "share": 1.2,
            "search": 0.1,
            "watch": 0.7,
            "complete": 1.2,
        }
        interaction_type = serializer.validated_data['interaction_type']

        # interactions that those count are importent
        if interaction_type in ["view", "comment", "search"]:
            Interaction.objects.create(
                user=request.user,
                movie=movie,
                interaction_type=interaction_type,
                weight=weights[interaction_type],
            )
        # interactions that those count are not importent
        elif interaction_type in ["like", "save", "share", "watch", "complete"]:
            Interaction.objects.get_or_create(
                user=request.user,
                movie=movie,
                interaction_type=interaction_type,
                weight=weights[interaction_type],
            )

        # don't need to return interaction object
        return Response({"Success": "Interaction created successfully."}, status=status.HTTP_201_CREATED)
