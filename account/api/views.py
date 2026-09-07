from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from account.api.serializers import (
    LoginSerializer,
    LogoutSerializer,
    TokenResponseSerializer,
    CreateUserSerializer,
    UserDetailSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.views import TokenRefreshView
from api_template import FilmBazAPI


class UserLoginAPI(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses=TokenResponseSerializer,
        tags=["Authentication"]
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


class UserLogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: None
        },
        tags=["Authentication"]
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
    tags=["Authentication"]
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


class CreateUserApi(FilmBazAPI):
    @extend_schema(
        description="ساخت کاربر جدید",
        request=CreateUserSerializer,
        responses={201: UserDetailSerializer, 400: CreateUserSerializer.errors},
        examples=[
            OpenApiExample(
                name="ساخت کاربر",
                value={
                    "username": "davoodq12w",
                    "password": "davoodq12wpassword",
                    "phone": "09037246850",
                    "email": "davod.q12w@gmail.com",
                    "image": None
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
    ...
