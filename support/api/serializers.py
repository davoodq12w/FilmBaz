from rest_framework import serializers
from support.models import SupportSession, SupportMessage
from account.models import FilmBazUser
from drf_spectacular.utils import extend_schema_field


class BasicUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmBazUser
        fields = ["id", "username", "phone", "email"]


class SupportSessionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    supporter = serializers.SerializerMethodField()

    class Meta:
        model = SupportSession
        fields = ["id", "user", "supporter", "session_date", "status", "created_at"]

    @extend_schema_field(BasicUserInfoSerializer())
    def get_user(self, obj):
        if obj.user is not None:
            data = BasicUserInfoSerializer(obj.user).data
            return data
        return None

    @extend_schema_field(BasicUserInfoSerializer())
    def get_supporter(self, obj):
        if obj.supporter is not None:
            data = BasicUserInfoSerializer(obj.user).data
            return data
        return None


class SupportMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = ["sender", "session_id", "text", "is_seen", "created_at"]

    @extend_schema_field(BasicUserInfoSerializer())
    def get_sender(self, obj):
        if obj.sender is not None:
            data = BasicUserInfoSerializer(obj.sender).data
            return data
        return None


class SupportSessionDetailSerializer(serializers.Serializer):
    support_session = SupportSessionSerializer()
    messages = SupportMessageSerializer(many=True)
