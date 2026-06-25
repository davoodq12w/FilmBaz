from rest_framework import serializers

from .models import SupportSession, SupportMessage


class SupportMessageCreateSerializer(serializers.ModelSerializer):
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=SupportSession.objects.all(),
        source="session",
        write_only=True,
        error_messages={
            "required": "شناسه سشن الزامی است.",
            "does_not_exist": "سشن پشتیبانی پیدا نشد.",
            "incorrect_type": "شناسه سشن معتبر نیست.",
        }
    )

    text = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            "required": "متن پیام الزامی است.",
            "blank": "متن پیام نمی‌تواند خالی باشد.",
            "max_length": "متن پیام نمی‌تواند بیشتر از ۱۰۰۰ کاراکتر باشد.",
        }
    )

    class Meta:
        model = SupportMessage
        fields = [
            "session_id",
            "text",
        ]

    def validate(self, attrs):
        user = self.context.get("user")

        if user is None or not user.is_authenticated:
            raise serializers.ValidationError(
                "برای ارسال پیام باید وارد حساب کاربری شده باشید."
            )

        return attrs

    def validate_session_id(self, session):
        if session.status == SupportSession.Status.CLOSED:
            raise serializers.ValidationError(
                "این سشن بسته شده و امکان ارسال پیام وجود ندارد."
            )

        return session

    def create(self, validated_data):
        user = self.context.get("user")

        return SupportMessage.objects.create(
            sender=user,
            **validated_data
        )


class SupportSessionSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = SupportSession
        fields = ["username", "id", "status"]

    def get_username(self, obj):
        return obj.user.username if obj.user else None


class SupportMessageSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = ["session_id", "sender_id", "id", "text", "created_at", "is_seen", "is_admin"]

    def get_is_admin(self, obj):
        return obj.sender.is_superuser if obj.sender else None
