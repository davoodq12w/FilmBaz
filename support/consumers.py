import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .serializers import SupportMessageCreateSerializer


class SupportChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.session_id = self.scope['url_route']['kwargs'].get("support_session_id")

        self.group_name = f"user_session_{self.session_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            await self.send_error("داده‌ای ارسال نشده است.")
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("فرمت JSON معتبر نیست.")
            return

        event_type = data.get("type")

        if event_type == "create_support_message":
            await self.create_support_message(data)
            return

        await self.send_error("نوع درخواست معتبر نیست.")

    async def create_support_message(self, data):
        result = await self.validate_and_create_message(data)

        if not result["ok"]:
            await self.send_validation_error(result["errors"])
            return

    @database_sync_to_async
    def validate_and_create_message(self, data):
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
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": message,
        }, ensure_ascii=False))

    async def send_validation_error(self, errors):
        await self.send(text_data=json.dumps({
            "type": "validation_error",
            "errors": errors,
        }, ensure_ascii=False, default=str))

    async def support_chat_message(self, event):

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
