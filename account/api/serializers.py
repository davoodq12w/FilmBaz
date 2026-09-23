from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
import re
from django.contrib.auth import authenticate
from account.models import FilmBazUser, Ticket
from film.api.serializers import GenreSerializer
from film.models import Genre
from account.tasks import send_confirm_email


class LoginSerializer(serializers.Serializer):
    """
    Serializer for loging users.
    Performs fileld validations.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, username):
        """
        validations for username by regex.
        """
        is_valid = re.fullmatch(r"^[a-zA-Z0-9_]+$", username)

        if not is_valid:
            raise serializers.ValidationError("نام کاربری باید از اعداد و حروف انگلیسی و _ تشکیل شده باشد")

        return username

    def validate(self, data):
        """
        validations for user exiting. don't need to check again in views.
        """
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError(
                "نام کاربری یا رمز عبور اشتباه است."
            )

        data['user'] = user
        return data


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer used only for login tokens response and swagger docs.
    """
    refresh = serializers.CharField()
    access = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """
    Serializer used only for logout request.
    """
    refresh = serializers.CharField()


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer used for user registration.
    Performs field validation and stores the password securely.
    """

    password = serializers.CharField(min_length=8, write_only=True, required=True)
    # use_url argument for able to upload image
    image = serializers.ImageField(allow_null=True, use_url=True, required=False)

    class Meta:
        model = FilmBazUser
        fields = [
            "username", "password", "phone", "email", "image",
        ]

    def validate_username(self, username):
        """
        Validations for username by regex and check user existing.
        """
        is_valid = re.fullmatch(r"^[a-zA-Z0-9_]+$", username)

        if not is_valid:
            raise serializers.ValidationError("نام کاربری باید از اعداد و حروف انگلیسی و _ تشکیل شده باشد")

        if FilmBazUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("نام کاربری از قبل وجود دارد")

        return username

    def validate_phone(self, phone):
        """
        Validations for phone number.
        """

        if not phone.isdigit():
            raise serializers.ValidationError('شماره تلفن باید فقط عدد باشد')

        if len(phone) != 11:
            raise serializers.ValidationError('تعداد ارقام باید 11 رقم باشد')

        if not phone.startswith('09'):
            raise serializers.ValidationError('شماره تلفن باید با 09 شروع شود')

        if FilmBazUser.objects.filter(phone=phone).exists():
            raise serializers.ValidationError('شماره تلفن درحال حاضر موجود میباشد')

        return phone

    def validate_email(self, email):
        """
        Validations for email address by using regex.
        """

        # using regex for simplify validations.
        is_valid = re.fullmatch(r'^(?:[a-zA-Z0-9_.]+@)(?:[a-zA-Z0-9_]+)\.(?:[a-zA-Z]{2,3})$', email)

        if not is_valid:
            raise serializers.ValidationError("ایمیل درست نوشته نشده است")

        if FilmBazUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("ایمیل از قبل وجود دارد")

        return email

    def create(self, validated_data):
        """
        creating user with hashed password.
        """
        password = validated_data.pop('password')

        user = FilmBazUser(**validated_data)
        # use set_password for auto hashing.
        user.set_password(password)
        user.save()

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for giving full detail of user object and changing details.
    Performs field vaildations for changing details.
    """

    # using SerializerMethodField for better details of object.
    favorite_genres = serializers.SerializerMethodField()
    # use_url argument for able to upload image.
    image = serializers.ImageField(allow_null=True, use_url=True, required=False)

    class Meta:
        model = FilmBazUser
        fields = [
            "id", "username", "phone", "email", "created",
            "image", "is_active", "is_staff", "is_superuser",
            "favorite_genres",
        ]
        read_only_fields = ["id", "favorite_genres", "is_active", "is_staff", "is_superuser", "created"]

    @extend_schema_field(GenreSerializer(many=True))
    def get_favorite_genres(self, user_obj):
        """
        giving better genres detail.
        """
        genres = user_obj.favorite_genres.all()
        if genres:
            # using GenreSerializer for serialized datas.
            return GenreSerializer(genres, many=True).data
        else:
            return []

    def validate_username(self, username):
        """
        validations for username by regex and check user exists.
        """
        is_valid = re.fullmatch(r"^[a-zA-Z0-9_]+$", username)

        if not is_valid:
            raise serializers.ValidationError("نام کاربری باید از اعداد و حروف انگلیسی و _ تشکیل شده باشد")
        if self.instance.id:
            if FilmBazUser.objects.filter(username=username).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("نام کاربری از قبل وجود دارد")
        else:
            if FilmBazUser.objects.filter(username=username).exists():
                raise serializers.ValidationError("نام کاربری از قبل وجود دارد")

        return username

    def validate_phone(self, phone):
        """
        validations for phone number and chech existing phone number.
        """
        if not phone.isdigit():
            raise serializers.ValidationError('شماره تلفن باید فقط عدد باشد')

        if len(phone) != 11:
            raise serializers.ValidationError('تعداد ارقام باید 11 رقم باشد')

        if not phone.startswith('09'):
            raise serializers.ValidationError('شماره تلفن باید با 09 شروع شود')

        if self.instance.id:
            if FilmBazUser.objects.filter(phone=phone).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('شماره تلفن درحال حاضر موجود میباشد')
        else:
            if FilmBazUser.objects.filter(phone=phone).exists():
                raise serializers.ValidationError('شماره تلفن درحال حاضر موجود میباشد')

        return phone

    def validate_email(self, email):
        """
        validations for email address by regex and chech existing email address.
        """

        # using regex for simplfy validations
        is_valid = re.fullmatch(r'^(?:[a-zA-Z0-9_.]+@)(?:[a-zA-Z0-9_]+)\.(?:[a-zA-Z]{2,3})$', email)

        if not is_valid:
            raise serializers.ValidationError("ایمیل درست نوشته نشده است")

        if self.instance.id:
            if FilmBazUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("ایمیل از قبل وجود دارد")
        else:
            if FilmBazUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("ایمیل از قبل وجود دارد")

        return email


class UserGenresSerializer(serializers.Serializer):
    """
    Serializer for user favorite genres.
    Performs field validation.
    """

    # use PrimaryKeyRelatedField for auto checking object exists in database or not.
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
    )

    def validate_genre_ids(self, value):

        # checking if there is a duplicate id or not
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "ژانر تکراری ارسال شده است."
            )

        # checking true lengh of ids.
        if not 3 <= len(set(value)) <= 5:
            raise serializers.ValidationError(
                "باید بین ۳ تا ۵ ژانر انتخاب کنید."
            )
        return value


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for user tickets.
    Performs field validation.
    """

    class Meta:
        model = Ticket
        fields = ['subject', 'text']

    def validate_subject(self, subject):
        """
        validations for subject. are they in enumirate or not?
        """
        subjects = [
            "Criticism",
            "Proposal",
            "Report",
        ]
        if subject not in subjects:
            raise serializers.ValidationError("subject must be one of 'Criticism', 'Proposal', 'Report'")
        return subject

    def save(self, user: FilmBazUser):
        """
        creating tickets for user and send confirmation email.
        """
        data = {
            "subject": self.validated_data["subject"],
            "text": self.validated_data["text"],
            "phone": user.phone,
            "email": user.email,
        }
        Ticket.objects.create(**data)

        # sending an email with Celery
        # so that the task runs in the background and does not interfere with the method's work
        send_confirm_email.delay(user.username, user.email)
        return None


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for user reset passwords.
    Performs email validation.
    """
    email = serializers.CharField(required=True)

    def validate_email(self, email):
        """
        validations for email address by regex.
        """

        # using regex for simplfy email validations.
        is_valid = re.fullmatch(r'^(?:[a-zA-Z0-9_.]+@)(?:[a-zA-Z0-9_]+)\.(?:[a-zA-Z]{2,3})$', email)

        if not is_valid:
            raise serializers.ValidationError("ایمیل درست نوشته نشده است")

        return email


class ConfirmResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for confirming user reset passwords.
    Performs passwords validation.
    """
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    # using confirm password for directly api usege
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        validations for matching passwords.
        """
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for user changing passwords.
    Performs passwords validation.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        validations for matching passwords.
        """
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return attrs
