from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from account.api.serializers import (
    LoginSerializer,
    LogoutSerializer,
    TokenResponseSerializer,
    CreateUserSerializer,
    UserDetailSerializer,
    UserGenresSerializer,
    TicketSerializer,
    ResetPasswordSerializer,
    ConfirmResetPasswordSerializer,
    ChangePasswordSerializer,
)
from account.models import FilmBazUser
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.views import TokenRefreshView
from api_template import FilmBazAPI
from film.api.serializers import (
    GenreSerializer,
    MovieSerializer,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from account.tasks import send_reset_password_email


class UserLoginApi(FilmBazAPI):
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


class UserLogoutApi(FilmBazAPI):

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
                request_only=True,
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
                request_only=True,
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
            },
            request_only=True,
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

    @extend_schema(
        description="ارسال تیکت",
        request=TicketSerializer,
        responses={200: {"Success": "ticket created."}},
        examples=[OpenApiExample(
            name="موضوع و متن تیکت",
            value={
                "subject": "Criticism",
                "text": "سایتتون زیادی خوبه."
            },
            request_only=True,
        )]
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response({"Success": "ticket created."}, status=status.HTTP_201_CREATED)


class UserSavesApi(FilmBazAPI):

    @extend_schema(
        description="گرفتن فیلم های ذخیره شده توسط کاربر",
        responses={200: MovieSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        movies = request.user.saves.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLikesApi(FilmBazAPI):

    @extend_schema(
        description="گرفتن فیلم های لایک شده توسط کاربر",
        responses={200: MovieSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        movies = request.user.likes.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordApi(FilmBazAPI):
    permission_classes = []

    @extend_schema(
        description="درخواست ریست کردن پسوورد کاربر",
        request=ResetPasswordSerializer,
        responses={200: {"detail": "If an account with this email exists, a password reset email has been sent."}},
        examples=[OpenApiExample(
            name="ارسال ایمیل کاربر",
            value={
                "email": "davod.q12w@gmail.com",
            },
            request_only=True,
        )],
        tags=["password"]
    )
    def post(self, request: Request, *args, **kwargs):

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = FilmBazUser.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            send_reset_password_email.delay(email=email, token=token, uid=uid)

        except FilmBazUser.DoesNotExist:
            pass

        return Response({
            "detail": "If an account with this email exists, a password reset email has been sent."
        }, status=status.HTTP_200_OK)


class ConfirmResetPasswordApi(FilmBazAPI):
    permission_classes = []

    @extend_schema(
        description="ریست کردن پسوورد کاربر",
        request=ConfirmResetPasswordSerializer,
        responses={200: {"Success": "password changed."}},
        examples=[OpenApiExample(
            name="دیتای لازم برای ریست پسوورد",
            value={
                "uid": "EXM",
                "token": "adfljuqwehasdgh235hohsdf8y23qgh",
                "password": "Str0ngP@ssw0rd",
                "confirm_password": "Str0ngP@ssw0rd"
            },
            request_only=True,
        )],
        tags=["password"]
    )
    def post(self, request: Request, *args, **kwargs):

        serializer = ConfirmResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        user_id = force_str(urlsafe_base64_decode(uid))

        try:
            user = FilmBazUser.objects.get(id=user_id)
            if not default_token_generator.check_token(user, token):
                return Response({
                    "Error": "sended data is incorrect."
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.save()

            return Response({
                "Success": "password changed."
            }, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError, FilmBazUser.DoesNotExist):
            return Response({
                "Error": "sended data is incorrect."
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordApi(FilmBazAPI):

    @extend_schema(
        description="عوض کردن پسوورد کاربر",
        request=ChangePasswordSerializer,
        responses={200: {"Success": "password changed."}},
        examples=[OpenApiExample(
            name="دیتای لازم برای عوض کردن پسوورد",
            value={
                "old_password": "0ldP@assw0rd",
                "new_password": "Str0ngP@ssw0rd",
                "confirm_password": "Str0ngP@ssw0rd"
            },
            request_only=True,
        )],
        tags=["password"],

    )
    def post(self, request: Request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data["old_password"]
        if not request.user.check_password(old_password):
            return Response({"Error": "current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(serializer.validated_data["new_password"])
        return Response({"Success": "password changed."}, status=status.HTTP_200_OK)
