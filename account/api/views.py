from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from account.api.serializers import (
    LoginSerializer,
    LogoutSerializer,
    TokenResponseSerializer,
    CreateUserSerializer,
    UserDetailSerializer,
    UserGenresSerializer, TicketSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.views import TokenRefreshView
from api_template import FilmBazAPI
from film.api.serializers import GenreSerializer


class UserLoginApi(APIView):
    permission_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses=TokenResponseSerializer,
        tags=["authentication"]
    )
    def post(self, request: Request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK
        )


class UserLogoutApi(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: None
        },
        tags=["authentication"]
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = RefreshToken(
            serializer.validated_data["refresh"]
        )

        token.blacklist()

        return Response(
            {
                "detail": "Logged out"
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=["authentication"]
)
class CustomTokenRefreshApi(TokenRefreshView):
    pass


class CreateUserApi(FilmBazAPI):
    permission_classes = []

    @extend_schema(
        description="ساخت کاربر جدید",
        request=CreateUserSerializer,
        responses={201: UserDetailSerializer},
        examples=[
            OpenApiExample(
                name="دیتا های اولیه کاربر",
                value={
                    "username": "davoodq12w",
                    "password": "davoodq12wpassword",
                    "phone": "09037246850",
                    "email": "davod.q12w@gmail.com",
                    "image": "optional",
                },
            ),
        ]
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = serializer.create(validated_data)

        return Response(UserDetailSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailApi(FilmBazAPI):

    @extend_schema(
        description="گرفتن اطلاعات کاربر",
        responses={200: UserDetailSerializer},
    )
    def get(self, request: Request, pk=None, *args, **kwargs):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="تغییر اطلاعات کاربر",
        request=UserDetailSerializer,
        responses={200: UserDetailSerializer},
        examples=[
            OpenApiExample(
                name="دیتا های قابل تغییر کاربر",
                value={
                    "username": "davoodq12w",
                    "phone": "09037246850",
                    "email": "davod.q12w@gmail.com",
                    "image": "optional",
                },
            ),
        ]
    )
    def put(self, request: Request, *args, **kwargs):
        serializer = UserDetailSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()

        return Response(UserDetailSerializer(updated_user).data, status=status.HTTP_200_OK)


class UserGenresApi(FilmBazAPI):

    @extend_schema(
        description="گرفتن ژانر های مورد علاقه کاربر",
        responses={200: GenreSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        genres = request.user.favorite_genres.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="تغییر ژانر های مورد علاقه کاربر",
        request=UserGenresSerializer,
        responses={200: GenreSerializer(many=True)},
        examples=[OpenApiExample(
            name="لیستی از آیدی های ژانر ها",
            value={
                "genre_ids": [1, 2, 3, 4, 5]
            }
        )]
    )
    def put(self, request: Request, *args, **kwargs):
        user_genres_serializer = UserGenresSerializer(data=request.data)
        user_genres_serializer.is_valid(raise_exception=True)

        genres = user_genres_serializer.validated_data["genre_ids"]
        request.user.favorite_genres.set(genres)

        genre_serializer = GenreSerializer(genres, many=True)
        return Response(genre_serializer.data, status=status.HTTP_200_OK)


class TicketApi(FilmBazAPI):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="ارسال تیکت",
        request=TicketSerializer,
        responses={200: {"Success": "ticket created."}},
        examples=[OpenApiExample(
            name="موضوع و متن تیکت",
            value={
                "subject": "Criticism",
                "text": "سایتتون زیادی خوبه."
            }
        )]
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response({"Success": "ticket created."}, status=status.HTTP_201_CREATED)
