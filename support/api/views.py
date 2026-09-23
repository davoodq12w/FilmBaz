from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from api_template import FilmBazAPI
from support.api.serializers import (
    SupportSessionSerializer,
    SupportSessionDetailSerializer,
)
from support.models import SupportSession, SupportMessage
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from django.db import transaction


class AdminSupportSessionsApi(FilmBazAPI):

    @extend_schema(
        description="گرفتن لیست سشن های پشتیبانی خالی و یا مربوط به اون پشتیبان ( فقط ادمین ها)",
        responses={200: SupportSessionSerializer(many=True), 403: "Forbidden"},
    )
    def get(self, request: Request, *args, **kwargs):
        if not request.user.is_superuser or not request.user.is_staff:
            return Response({"Error": "this action only for admins."}, status=status.HTTP_403_FORBIDDEN)

        support_sessions = SupportSession.objects.filter(
            Q(supporter=request.user) | Q(supporter__isnull=True),
            status__in=[
                SupportSession.Status.OPEN,
                SupportSession.Status.PENDING,
            ]
        )

        serializer = SupportSessionSerializer(support_sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminSupportSessionDetailsApi(FilmBazAPI):

    @extend_schema(
        description="گرفتن جزییات کامل و پیام های سشن های پشتیبانی خالی و یا مربوط به اون پشتیبان ( فقط ادمین ها)"
                    "(با درخواست به این api تمامی پیام های خوانده نشده به خوانده شده تغییر وضعیت میدهند.)",
        responses={200: SupportSessionSerializer(many=True), 403: "Forbidden", 400: "Bad Request"},
    )
    def get(self, request: Request, pk=None, *args, **kwargs):
        if not request.user.is_superuser or not request.user.is_staff:
            return Response({"Error": "this action only for admins."}, status=status.HTTP_403_FORBIDDEN)

        if not pk:
            return Response({"Error": "Support Session id most be given."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            support_session = SupportSession.objects.filter(id=pk).first()

            if support_session is None:
                return Response({"Error": "Support Session with this data is not exists."},
                                status=status.HTTP_400_BAD_REQUEST)

            if support_session.supporter.id not in [None, request.user.id]:
                return Response({"Error": "Supporter of this Session is someone else."},
                                status=status.HTTP_403_FORBIDDEN)

            support_session.supporter = request.user
            support_session.status = SupportSession.Status.OPEN
            support_session.save(update_fields=["supporter", "status"])

            SupportMessage.objects.filter(session=support_session, is_seen=False).update(is_seen=True)
            messages = SupportMessage.objects.filter(session=support_session).order_by("created_at")
            data = {
                "support_session": support_session,
                "messages": messages
            }

            serializer = SupportSessionDetailSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)


class SupportSessionDetailsApi(FilmBazAPI):

    @extend_schema(
        description="گرفتن جزییات کامل و پیام های سشن پشتیبانی مربوط به اون یوزر ( فقط یوزرها)",
        responses={200: SupportSessionSerializer(many=True), 403: "Forbidden", 400: "Bad Request"},
    )
    def get(self, request: Request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return Response({"Error": "this action not for admins."}, status=status.HTTP_403_FORBIDDEN)

        support_session = SupportSession.objects.filter(
            user=request.user,
            status__in=[
                SupportSession.Status.OPEN,
                SupportSession.Status.PENDING,
            ]
        ).first()
        if support_session is None:
            data = {
                "user": request.user,
                "supporter": None,
                "status": SupportSession.Status.PENDING,
            }
            support_session = SupportSession.objects.create(**data)

        messages = SupportMessage.objects.filter(session=support_session).order_by("created_at")
        data = {
            "support_session": support_session,
            "messages": messages
        }

        serializer = SupportSessionDetailSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupportSocketDocs(FilmBazAPI):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        description="""
        ## WebSocket

        URL:

        ws://localhost:8000/ws/support/{session_id}/

        ### Client -> Server

        ```json
        {
            "type": "create_support_message",
            "message": "سلام"
        }
        ```

        ### Server -> Client

        ```json
        {
            "type": "support_chat_message",
            "session_id": "integer",
            "user_id": "integer",
            "support_id": "integer | none",
            "message_id": "integer",
            "message_text": "string",
            "message_timestamp": "datetime",
            "message_is_seen": "boolien",
            "is_admin": "boolien",
        }
        ```
        """,
        responses=None
    )
    def get(self, request):
        pass
