from django.test import TestCase
from account.models import FilmBazUser
from support.models import SupportSession, SupportMessage
from support.serializers import SupportMessageCreateSerializer, SupportSessionSerializer, SupportMessageSerializer
from model_bakery import baker
from unittest.mock import patch

class SupportMessageCreateSerializerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._p1 = patch("support.signals.send_message_to_chat.delay", return_value=None)
        cls._p1.start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._p1.stop()

    @classmethod
    def setUpTestData(cls):
        cls.user1 = baker.make(
            FilmBazUser,
            username="user1",
            phone="09000000001",
            email="user1@gmail.com"
        )
        cls.user1.set_password("testpass")
        cls.user1.save()

        cls.user2 = baker.make(
            FilmBazUser,
            username="user2",
            phone="09000000002",
            email="user2@gmail.com"
        )
        cls.user2.set_password("testpass")
        cls.user2.save()

        cls.open_session = baker.make(
            SupportSession,
            id=1,
            user=cls.user1,
            status=SupportSession.Status.OPEN,
        )

        cls.closed_session = baker.make(
            SupportSession,
            id=2,
            user=cls.user2,
            status=SupportSession.Status.CLOSED,
        )

    def test_validate_fails_when_user_missing_in_context(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": self.open_session.id, "text": "سلام"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "برای ارسال پیام باید وارد حساب کاربری شده باشید."
        )

    def test_validate_fails_when_user_not_authenticated(self):
        class DummyUnauthenticatedUser:
            is_authenticated = False

        serializer = SupportMessageCreateSerializer(
            data={"session_id": self.open_session.id, "text": "سلام"},
            context={"user": DummyUnauthenticatedUser()}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "برای ارسال پیام باید وارد حساب کاربری شده باشید."
        )

    def test_session_id_required(self):
        serializer = SupportMessageCreateSerializer(
            data={"text": "hello"},
            context={"user": self.user1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("session_id", serializer.errors)
        self.assertEqual(serializer.errors["session_id"][0], "شناسه سشن الزامی است.")

    def test_session_id_incorrect_type(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": "abc", "text": "hello"},
            context={"user": self.user1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("session_id", serializer.errors)
        self.assertEqual(serializer.errors["session_id"][0], "شناسه سشن معتبر نیست.")

    def test_session_id_not_found(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": 999999, "text": "hello"},
            context={"user": self.user1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("session_id", serializer.errors)
        self.assertEqual(serializer.errors["session_id"][0], "سشن پشتیبانی پیدا نشد.")

    def test_text_required(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": self.open_session.id},
            context={"user": self.user1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertEqual(serializer.errors["text"][0], "متن پیام الزامی است.")

    def test_text_blank(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": self.open_session.id, "text": ""},
            context={"user": self.user1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertEqual(serializer.errors["text"][0], "متن پیام نمی‌تواند خالی باشد.")

    def test_text_max_length(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": self.open_session.id, "text": "a" * 1001},
            context={"user": self.user1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertEqual(
            serializer.errors["text"][0],
            "متن پیام نمی‌تواند بیشتر از ۱۰۰۰ کاراکتر باشد."
        )

    def test_create_success(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": self.open_session.id, "text": "پیام تست"},
            context={"user": self.user1}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        message = serializer.save()

        self.assertIsInstance(message, SupportMessage)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.session, self.open_session)
        self.assertEqual(message.text, "پیام تست")

    def test_closed_session_fails(self):
        serializer = SupportMessageCreateSerializer(
            data={"session_id": self.closed_session.id, "text": "hello"},
            context={"user": self.user1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("session_id", serializer.errors)
        self.assertEqual(
            serializer.errors["session_id"][0],
            "این سشن بسته شده و امکان ارسال پیام وجود ندارد."
        )


class SupportSessionSerializerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._p1 = patch("support.signals.send_message_to_chat.delay", return_value=None)
        cls._p1.start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._p1.stop()

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(
            FilmBazUser,
            username="ali",
            phone="09000000011",
            email="ali@gmail.com"
        )

        cls.session_with_user = baker.make(
            SupportSession,
            user=cls.user,
            status=SupportSession.Status.OPEN
        )

        cls.session_without_user = baker.make(
            SupportSession,
            user=None,
            status=SupportSession.Status.PENDING
        )

    def test_username_serialized(self):
        data = SupportSessionSerializer(self.session_with_user).data

        self.assertEqual(data["username"], "ali")
        self.assertEqual(data["id"], self.session_with_user.id)
        self.assertEqual(data["status"], SupportSession.Status.OPEN)

    def test_username_none_when_user_is_none(self):
        data = SupportSessionSerializer(self.session_without_user).data

        self.assertIsNone(data["username"])
        self.assertEqual(data["id"], self.session_without_user.id)
        self.assertEqual(data["status"], SupportSession.Status.PENDING)


class SupportMessageSerializerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._p1 = patch("support.signals.send_message_to_chat.delay", return_value=None)
        cls._p1.start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._p1.stop()

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = baker.make(
            FilmBazUser,
            username="admin_user",
            phone="09000000021",
            email="admin@gmail.com",
            is_superuser=True,
            is_staff=True
        )

        cls.normal_user = baker.make(
            FilmBazUser,
            username="normal_user",
            phone="09000000022",
            email="normal@gmail.com",
            is_superuser=False
        )

        cls.session = baker.make(
            SupportSession,
            user=cls.normal_user,
            supporter=cls.admin_user,
            status=SupportSession.Status.OPEN
        )

        cls.message_by_admin = baker.make(
            SupportMessage,
            sender=cls.admin_user,
            session=cls.session,
            text="پیام ادمین",
            is_seen=False
        )

        cls.message_by_normal = baker.make(
            SupportMessage,
            sender=cls.normal_user,
            session=cls.session,
            text="پیام کاربر",
            is_seen=True
        )

        cls.message_without_sender = baker.make(
            SupportMessage,
            sender=None,
            session=cls.session,
            text="پیام بدون فرستنده",
            is_seen=False
        )

    def test_is_admin_true_for_superuser_sender(self):
        data = SupportMessageSerializer(self.message_by_admin).data
        self.assertTrue(data["is_admin"])

    def test_is_admin_false_for_normal_sender(self):
        data = SupportMessageSerializer(self.message_by_normal).data
        self.assertFalse(data["is_admin"])

    def test_is_admin_none_when_sender_is_none(self):
        data = SupportMessageSerializer(self.message_without_sender).data
        self.assertIsNone(data["is_admin"])

    def test_output_fields(self):
        data = SupportMessageSerializer(self.message_by_normal).data
        expected_fields = {"session_id", "sender_id", "id", "text", "created_at", "is_seen", "is_admin"}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serialized_values_match_model(self):
        data = SupportMessageSerializer(self.message_by_normal).data

        self.assertEqual(data["id"], self.message_by_normal.id)
        self.assertEqual(data["session_id"], self.session.id)
        self.assertEqual(data["sender_id"], self.normal_user.id)
        self.assertEqual(data["text"], "پیام کاربر")
        self.assertTrue(data["is_seen"])
