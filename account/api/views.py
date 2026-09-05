from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from account.api.serializers import (
    LoginSerializer,
    LogoutSerializer,
    TokenResponseSerializer
)
from drf_spectacular.utils import extend_schema


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
            }
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
            }
        )
