import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from account.models import FilmBazUser
from .models import SupportSession
from .serializers import SupportMessageCreateSerializer


class SupportChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer used for sending and receving support chat messages.
    only authenticated users can use this consumer.
    """

    async def connect(self):
        """
        Coroutine used to connect the user to support chat channel.
        take support_session_id and connect the user to support chat channel.
        """
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.session_id = self.scope['url_route']['kwargs'].get("support_session_id")

        # check user has permisson to connect the support session or not.
        valid, message = await self.validate_user_to_connect(self.user.id, self.session_id)
        if not valid:
            await self.send_validation_error(message)
            await self.close()
            return

        self.group_name = f"user_session_{self.session_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        coroutine used to disconnect the user from support chat channel.
        """
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        coroutine used for validate the request to create new support chat message.
        """
        if text_data is None:
            await self.send_error("text data most be exist.")
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("data most be valid JSON type.")
            return

        event_type = data.get("type")

        if event_type == "create_support_message":
            await self.create_support_message(data)
            return

        await self.send_error("event type is invalid.")

    async def create_support_message(self, data):
        """
        coroutine used for create new support chat message.
        """
        result = await self.validate_and_create_message(data)

        if not result["ok"]:
            await self.send_validation_error(result["errors"])
            return

    @database_sync_to_async
    def validate_user_to_connect(self, user_id, support_id):
        """
        method used for validate user to connection
        """
        user = FilmBazUser.objects.filter(id=user_id).first()
        if not user:
            return False, "user not exist."
        support_session = SupportSession.objects.filter(id=support_id).first()
        if not support_session:
            return False, "support session not exist."

        if support_session.status not in [SupportSession.Status.OPEN, SupportSession.Status.PENDING]:
            return False, "support session not active."

        if user.is_superuser and user.is_staff:
            if support_session.supporter_id not in [user.id, None]:
                return False, "support session has another supporter."

        else:
            if support_session.user_id != user.id:
                return False, "support session has another user."
        return True, "ok."

    @database_sync_to_async
    def validate_and_create_message(self, data):
        """
        method used for validate the data of request to create new support chat message.
        """
        serializer = SupportMessageCreateSerializer(
            data=data,
            context={
                "user": self.user,
            }
        )

        if not serializer.is_valid():
            return {
                "ok": False,
                "errors": serializer.errors,
            }

        serializer.save()

        return {
            "ok": True,
        }

    async def send_error(self, message):
        """
        coroutine used to send error message.
        """
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": message,
        }, ensure_ascii=False))

    async def send_validation_error(self, errors):
        """
        coroutine used to send validation error message.
        """
        await self.send(text_data=json.dumps({
            "type": "validation_error",
            "errors": errors,
        }, ensure_ascii=False, default=str))

    async def support_chat_message(self, event):
        """
        coroutine used to send support chat message.
        """
        await self.send(text_data=json.dumps({
            "type": "support_chat_message",
            "session_id": event.get("session_id"),
            "user_id": event.get("user_id"),
            "support_id": event.get("support_id"),
            "message_id": event.get("message_id"),
            "message_text": event.get("message_text"),
            "message_timestamp": event.get("message_timestamp"),
            "message_is_seen": event.get("message_is_seen"),
            "is_admin": event.get("is_admin"),
        }))
