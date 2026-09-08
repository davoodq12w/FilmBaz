from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
import re
from django.contrib.auth import authenticate
from account.models import FilmBazUser, Ticket
from film.api.serializers import GenreSerializer
from film.models import Genre
from account.tasks import send_confirm_email


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, username):
        is_valid = re.fullmatch(r"^[a-zA-Z0-9_]+$", username)

        if not is_valid:
            raise serializers.ValidationError("نام کاربری باید از اعداد و حروف انگلیسی و _ تشکیل شده باشد")

        return username

    def validate(self, data):

        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError(
                "نام کاربری یا رمز عبور اشتباه است."
            )

        data['user'] = user
        return data


class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    image = serializers.ImageField(allow_null=True, use_url=True, required=False)

    class Meta:
        model = FilmBazUser
        fields = [
            "username", "password", "phone", "email", "image",
        ]

    def validate_username(self, username):
        is_valid = re.fullmatch(r"^[a-zA-Z0-9_]+$", username)

        if not is_valid:
            raise serializers.ValidationError("نام کاربری باید از اعداد و حروف انگلیسی و _ تشکیل شده باشد")

        if FilmBazUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("نام کاربری از قبل وجود دارد")

        return username

    def validate_phone(self, phone):

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
        is_valid = re.fullmatch(r'^(?:[a-zA-Z0-9_.]+@)(?:[a-zA-Z0-9_]+)\.(?:[a-zA-Z]{2,3})$', email)

        if not is_valid:
            raise serializers.ValidationError("ایمیل درست نوشته نشده است")

        if FilmBazUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("ایمیل از قبل وجود دارد")

        return email

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = FilmBazUser(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    favorite_genres = serializers.SerializerMethodField()
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
        genres = user_obj.favorite_genres.all()
        if genres:
            return GenreSerializer(genres, many=True).data
        else:
            return []

    def validate_username(self, username):
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
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
    )

    def validate_genre_ids(self, value):

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "ژانر تکراری ارسال شده است."
            )

        if not 3 <= len(set(value)) <= 5:
            raise serializers.ValidationError(
                "باید بین ۳ تا ۵ ژانر انتخاب کنید."
            )
        return value


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['subject', 'text']

    def validate_subject(self, subject):
        subjects = [
            "Criticism",
            "Proposal",
            "Report",
        ]
        if subject not in subjects:
            raise serializers.ValidationError("subject must be one of 'Criticism', 'Proposal', 'Report'")
        return subject

    def save(self, user: FilmBazUser):
        data = {
            "subject": self.validated_data["subject"],
            "text": self.validated_data["text"],
            "phone": user.phone,
            "email": user.email,
        }
        Ticket.objects.create(**data)
        send_confirm_email.delay(user.username, user.email)
        return None
