from rest_framework import serializers
import re
from django.contrib.auth import authenticate


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
