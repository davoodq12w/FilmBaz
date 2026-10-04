from rest_framework import serializers
from .models import SupportSession, SupportMessage


class SupportMessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used for creating support messages.
    perform validations of data.
    """
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=SupportSession.objects.all(),
        source="session",
        write_only=True,
        error_messages={
            "required": "session_id is required.",
            "does_not_exist": "session with this id does not exist.",
            "incorrect_type": "session id is an integer.",
        }
    )

    text = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            "required": "text of message is required.",
            "blank": "message can't be blank.",
            "max_length": "text of message is over 1000 characters.",
        }
    )

    class Meta:
        model = SupportMessage
        fields = [
            "session_id",
            "text",
        ]

    def validate(self, attrs):
        """
        method used for validate user.
        """
        user = self.context.get("user")

        if user is None or not user.is_authenticated:
            raise serializers.ValidationError(
                "user most be authenticated."
            )

        return attrs

    def validate_session_id(self, session):
        """
        method used for validate session activation.
        """
        if session.status == SupportSession.Status.CLOSED:
            raise serializers.ValidationError(
                "support session is already closed."
            )

        return session

    def create(self, validated_data):
        """
        method used for create support message.
        """
        user = self.context.get("user")

        return SupportMessage.objects.create(
            sender=user,
            **validated_data
        )


class SupportSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for Sessions
    """
    username = serializers.SerializerMethodField()

    class Meta:
        model = SupportSession
        fields = ["username", "id", "status"]

    def get_username(self, obj):
        """
        method used for get username.
        """
        return obj.user.username if obj.user else None


class SupportMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Messages
    """
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = ["session_id", "sender_id", "id", "text", "created_at", "is_seen", "is_admin"]

    def get_is_admin(self, obj):
        """
        method used for get is_admin of message sender.
        """
        return obj.sender.is_superuser if obj.sender else None
