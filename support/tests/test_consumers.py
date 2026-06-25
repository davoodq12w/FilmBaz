import json
import asyncio
from django.test import TransactionTestCase, override_settings
from model_bakery import baker
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from account.models import FilmBazUser
from support.models import SupportSession, SupportMessage
from support.consumers import SupportChatConsumer
from django.urls import re_path
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from unittest.mock import patch
from contextlib import suppress


test_application = URLRouter([
    re_path(r"^ws/support_chat/(?P<support_session_id>\d+)/$", SupportChatConsumer.as_asgi()),
])


@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
class SupportChatConsumerTestCase(TransactionTestCase):

    @database_sync_to_async
    def _messages_count(self):
        return SupportMessage.objects.count()

    @database_sync_to_async
    def _latest_message(self):
        return SupportMessage.objects.latest("id")

    @classmethod
    def setUpClass(cls):
        cls._p1 = patch("support.signals.send_message_to_chat.delay", return_value=None)
        cls._p1.start()
        super().setUpClass()
        cls._communicators = []

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._p1.stop()

    def setUp(self):
        self.user = baker.make(
            FilmBazUser,
            username="user1",
            phone="09000000111",
            email="user1@test.com",
        )
        self.user.set_password("testpass")
        self.user.save()

        self.other_user = baker.make(
            FilmBazUser,
            username="user2",
            phone="09000000112",
            email="user2@test.com",
        )

        self.open_session = baker.make(
            SupportSession,
            user=self.user,
            status=SupportSession.Status.OPEN,
        )

        self.closed_session = baker.make(
            SupportSession,
            user=self.other_user,
            status=SupportSession.Status.CLOSED,
        )

    async def _connect(self, session_id, user):
        communicator = WebsocketCommunicator(
            test_application,
            f"/ws/support_chat/{session_id}/"
        )
        communicator.scope["user"] = user
        connected, _ = await communicator.connect()
        self.__class__._communicators.append(communicator)
        return communicator, connected

    async def test_connect_fails_for_anonymous_user(self):
        class DummyAnonymous:
            is_authenticated = False

        communicator, connected = await self._connect(self.open_session.id, DummyAnonymous())
        self.assertFalse(connected)

    async def test_connect_success_for_authenticated_user(self):
        communicator, connected = await self._connect(self.open_session.id, self.user)
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_receive_without_text_data_sends_error(self):
        communicator, connected = await self._connect(self.open_session.id, self.user)
        self.assertTrue(connected)

        await communicator.send_to(bytes_data=b"abc")
        response = await communicator.receive_from()
        payload = json.loads(response)

        self.assertEqual(payload["type"], "error")
        self.assertEqual(payload["message"], "داده‌ای ارسال نشده است.")

        await communicator.disconnect()

    async def test_receive_invalid_json_sends_error(self):
        communicator, connected = await self._connect(self.open_session.id, self.user)
        self.assertTrue(connected)

        await communicator.send_to(text_data="{bad json")
        response = await communicator.receive_from()
        payload = json.loads(response)

        self.assertEqual(payload["type"], "error")
        self.assertEqual(payload["message"], "فرمت JSON معتبر نیست.")

        await communicator.disconnect()

    async def test_receive_invalid_event_type_sends_error(self):
        communicator, connected = await self._connect(self.open_session.id, self.user)
        self.assertTrue(connected)

        await communicator.send_to(text_data=json.dumps({
            "type": "unknown_type"
        }, ensure_ascii=False))

        response = await communicator.receive_from()
        payload = json.loads(response)

        self.assertEqual(payload["type"], "error")
        self.assertEqual(payload["message"], "نوع درخواست معتبر نیست.")

        await communicator.disconnect()

    async def test_create_support_message_validation_error(self):
        communicator, connected = await self._connect(self.open_session.id, self.user)
        self.assertTrue(connected)

        await communicator.send_to(text_data=json.dumps({
            "type": "create_support_message",
            "session_id": self.open_session.id,
            "text": "",
        }, ensure_ascii=False))

        response = await communicator.receive_from()
        payload = json.loads(response)

        self.assertEqual(payload["type"], "validation_error")
        self.assertIn("errors", payload)
        self.assertIn("text", payload["errors"])

        await communicator.disconnect()

    async def test_create_support_message_success_creates_db_record(self):
        communicator, connected = await self._connect(self.open_session.id, self.user)
        self.assertTrue(connected)

        before_count = await self._messages_count()

        await communicator.send_to(text_data=json.dumps({
            "type": "create_support_message",
            "session_id": self.open_session.id,
            "text": "سلام تست",
        }, ensure_ascii=False))

        try:
            response = await communicator.receive_from(timeout=0.2)
        except asyncio.TimeoutError:
            response = None

        if response is not None:
            payload = json.loads(response)
            self.fail(f"Expected no immediate response in success path, got: {payload}")

        after_count = await self._messages_count()
        self.assertEqual(after_count, before_count + 1)

        msg = await self._latest_message()
        self.assertEqual(msg.sender_id, self.user.id)
        self.assertEqual(msg.session_id, self.open_session.id)
        self.assertEqual(msg.text, "سلام تست")

        with suppress(asyncio.CancelledError):
            await communicator.disconnect()

    async def test_create_support_message_closed_session_returns_validation_error(self):
        communicator, connected = await self._connect(self.closed_session.id, self.user)
        self.assertTrue(connected)

        await communicator.send_to(text_data=json.dumps({
            "type": "create_support_message",
            "session_id": self.closed_session.id,
            "text": "سلام",
        }, ensure_ascii=False))

        response = await communicator.receive_from()
        payload = json.loads(response)

        self.assertEqual(payload["type"], "validation_error")
        self.assertIn("session_id", payload["errors"])
        self.assertEqual(
            payload["errors"]["session_id"][0],
            "این سشن بسته شده و امکان ارسال پیام وجود ندارد."
        )

        await communicator.disconnect()

    async def test_support_chat_message_event_shape(self):
        communicator, connected = await self._connect(self.open_session.id, self.user)
        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"user_session_{self.open_session.id}",
            {
                "type": "support_chat_message",
                "session_id": self.open_session.id,
                "user_id": self.user.id,
                "support_id": None,
                "message_id": 10,
                "message_text": "hello",
                "message_timestamp": "2026-01-01T00:00:00Z",
                "message_is_seen": False,
                "is_admin": False,
            }
        )

        response = await communicator.receive_from()
        payload = json.loads(response)

        self.assertEqual(payload["type"], "support_chat_message")
        self.assertEqual(payload["session_id"], self.open_session.id)
        self.assertEqual(payload["user_id"], self.user.id)
        self.assertEqual(payload["message_text"], "hello")
        self.assertFalse(payload["is_admin"])

        await communicator.disconnect()
