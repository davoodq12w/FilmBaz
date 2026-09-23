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
from rest_framework.permissions import AllowAny


class UserLoginApi(FilmBazAPI):
    """
    user LogIn api view.
    all users access to the view.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        description="وارد شدن کاربر به سیستم. زمان انقضای توکن ها :( توکن دسترسی : 15 دقیقه)(توکن بازیابی : 7 روز)",
        request=LoginSerializer,
        responses=TokenResponseSerializer,
        tags=["authentication"]
    )
    def post(self, request: Request):
        """
        used for user login.
        take username and password and givig jwt tokens for header of requests.
        """
        serializer = LoginSerializer(data=request.data)

        # raise_exception argument for raising the errors without any Additional code
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # get token object for the user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK
        )


class UserLogoutApi(FilmBazAPI):
    """
    user LogOut api view.
    only authenticated users access to the view.
    """

    @extend_schema(
        description="خارج شدن کاربر از سیستم."
                    " توجه کنید که کاربر هنوز میتواند تا زمان انتضای توکن دسترسی با اون توکن وارد سیستم شود( زمان انقصا 15 دقیقه)",
        request=LogoutSerializer,
        responses={
            200: None
        },
        tags=["authentication"]
    )
    def post(self, request):
        """
        used for user loging out.
        take refresh token of the user and block the token.
        warrning: user can still loged in with the access token of refresh token until access token expired(15min).
        """
        serializer = LogoutSerializer(data=request.data)

        # raise_exception argument for raising the errors without any Additional code
        serializer.is_valid(raise_exception=True)

        # geting token from refresh token
        token = RefreshToken(
            serializer.validated_data["refresh"]
        )

        # block the token
        token.blacklist()

        return Response(
            {
                "detail": "Logged out"
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    description="گرفتن توکن دسترسی جدید با استفاده از توکن بازیابی."
                "زمان انقضای توکن ها :( توکن دسترسی : 15 دقیقه)(توکن بازیابی : 7 روز)",
    tags=["authentication"]
)
class CustomTokenRefreshApi(TokenRefreshView):
    pass


class CreateUserApi(FilmBazAPI):
    """
    creating user api view.
    only new users can make user.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

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
        """
        creating new user.
        take new user information and giving full info of the new user.
        """
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # use create method of serializer for hashing the password and eseier creation.
        user = serializer.create(validated_data)

        return Response(UserDetailSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailApi(FilmBazAPI):
    """
    user detail api view. get and change info of users.
    only authenticated users access the view.
    """

    @extend_schema(
        description="گرفتن اطلاعات کاربر",
        responses={200: UserDetailSerializer},
    )
    def get(self, request: Request, *args, **kwargs):
        """
        get full detail of user.
        giving the full info of user.
        """
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
        """
        change detail of user.
        take user new information and giving the new full info of user.
        """
        serializer = UserDetailSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)

        # saving the new info by using the save method and instance argument of serializer
        updated_user = serializer.save()

        return Response(UserDetailSerializer(updated_user).data, status=status.HTTP_200_OK)


class UserGenresApi(FilmBazAPI):
    """
    user favorite genres api view.
    only authenticated users access the view.
    """

    @extend_schema(
        description="گرفتن ژانر های مورد علاقه کاربر",
        responses={200: GenreSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        """
        giving favorite genres of user.
        """
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
        """
        change favorite genres of user.
        take a list of user new favorite genre ids and giving new iformations of user favorite genres.
        """
        user_genres_serializer = UserGenresSerializer(data=request.data)
        user_genres_serializer.is_valid(raise_exception=True)

        genres = user_genres_serializer.validated_data["genre_ids"]

        # useing set method for replace the genres
        request.user.favorite_genres.set(genres)

        genre_serializer = GenreSerializer(genres, many=True)
        return Response(genre_serializer.data, status=status.HTTP_200_OK)


class TicketApi(FilmBazAPI):
    """
    create ticket api view.
    only authenticated users access the view.
    """

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
        """
        create new ticket for user.
        take data of new ticket and send conformation email by using serializer.
        """
        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response({"Success": "ticket created."}, status=status.HTTP_201_CREATED)


class UserSavesApi(FilmBazAPI):
    """
    get user saved movies api view.
    only authenticated users access the view.
    """

    @extend_schema(
        description="گرفتن فیلم های ذخیره شده توسط کاربر",
        responses={200: MovieSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        """
        giving saved movies of user.
        """
        movies = request.user.saves.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLikesApi(FilmBazAPI):
    """
    get user liked movies api view.
    only authenticated users access the view.
    """

    @extend_schema(
        description="گرفتن فیلم های لایک شده توسط کاربر",
        responses={200: MovieSerializer(many=True)},
    )
    def get(self, request: Request, *args, **kwargs):
        """
        giving liked movies of user.
        """
        movies = request.user.likes.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordApi(FilmBazAPI):
    """
    reset password api view.
    all users access the view.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

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
        """
        reseting password by using email.
        take email address and send password reset email to the given email address.
        """
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            # get user of email
            user = FilmBazUser.objects.get(email=email)

            # creating uid and token for the user of email
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # send email of reset password by celery
            # if person who requested reset password is access to the email inbox he can change the password.
            send_reset_password_email.delay(email=email, token=token, uid=uid)

        except FilmBazUser.DoesNotExist:
            pass

        # return a scure response to unauthenticated user.
        return Response({
            "detail": "If an account with this email exists, a password reset email has been sent."
        }, status=status.HTTP_200_OK)


class ConfirmResetPasswordApi(FilmBazAPI):
    """
    reset password api view.
    all users access the view.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

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
        """
        changing user password by reset password request.
        take token and uid and new password and then change the account password.
        """

        serializer = ConfirmResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # uid is stringify of user id
        uid = serializer.validated_data["uid"]

        # token is specefic for every user
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        # get user id by uid
        user_id = force_str(urlsafe_base64_decode(uid))

        try:
            user = FilmBazUser.objects.get(id=user_id)

            # check the matching of token and user
            if not default_token_generator.check_token(user, token):
                return Response({
                    "Error": "sended data is incorrect."
                }, status=status.HTTP_400_BAD_REQUEST)

            # set new hashed password
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
    """
    changeing password api view.
    only authenticated users can use this view.
    """

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
        """
        changing user password.
        take old and new password and then change the account password.
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # checking if the current password is correct or not.
        old_password = serializer.validated_data["old_password"]
        if not request.user.check_password(old_password):
            return Response({"Error": "current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # set new hashed password
        request.user.set_password(serializer.validated_data["new_password"])
        return Response({"Success": "password changed."}, status=status.HTTP_200_OK)
