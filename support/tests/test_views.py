from django.test import Client, TestCase
from model_bakery import baker
from account.models import FilmBazUser
from django.shortcuts import reverse
from support.models import SupportSession, SupportMessage
from support.serializers import SupportSessionSerializer, SupportMessageSerializer
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from freezegun import freeze_time
from unittest.mock import patch


class SupportSessionViewTest(TestCase):
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
            username='user',
            phone="09000000001",
            email="user@gmail.com"
        )
        cls.user.set_password("testpass")
        cls.user.save()

        cls.another_user = baker.make(
            FilmBazUser,
            username='another_user',
            phone="09000000002",
            email="another_user@gmail.com"
        )
        cls.another_user.set_password("testpass")
        cls.another_user.save()

        cls.admin = baker.make(
            FilmBazUser,
            username='admin',
            phone="09000000003",
            email="admin@gmail.com"
        )
        cls.admin.set_password("testpass")
        cls.admin.is_superuser = True
        cls.admin.is_staff = True
        cls.admin.save()

        cls.another_admin = baker.make(
            FilmBazUser,
            username='another_admin',
            phone="09000000004",
            email="another_admin@gmail.com"
        )
        cls.another_admin.set_password("testpass")
        cls.another_admin.is_superuser = True
        cls.another_admin.is_staff = True
        cls.another_admin.save()

        yesterday = timezone.now() - timedelta(days=1)
        with freeze_time(yesterday):
            cls.open_session_support = baker.make(
                SupportSession,
                id=1,
                user=cls.another_user,
                supporter=cls.another_admin,
                status=SupportSession.Status.OPEN,
            )
        cls.pending_session_support = baker.make(
            SupportSession,
            id=2,
            user=cls.user,
            supporter=None,
            status=SupportSession.Status.PENDING,
        )
        with freeze_time(yesterday):
            cls.closed_session_support = baker.make(
                SupportSession,
                id=3,
                user=cls.user,
                supporter=None,
                status=SupportSession.Status.CLOSED,
            )
        for i in range(1, 11):
            baker.make(
                SupportMessage,
                sender=cls.user,
                session=cls.pending_session_support,
                text=f"message {i}",
                is_seen=True if i <= 5 else False,
            )

    def setUp(self):
        self.client = Client()
        self.url = reverse("support:get_support_session")

    def test_admin_user(self):
        self.client.login(username="admin", password="testpass")
        response = self.client.get(self.url)

        data = response.json()
        self.assertIn("user_type", data)
        self.assertEqual(data["user_type"], "admin")
        self.assertIn("ok", data)
        self.assertTrue(data["ok"])
        self.assertIn("sessions", data)
        sessions = SupportSessionSerializer(
            SupportSession.objects.filter(
                Q(supporter=self.admin) | Q(supporter__isnull=True),
                status__in=[
                    SupportSession.Status.OPEN,
                    SupportSession.Status.PENDING,
                ]
            ),
            many=True,
        ).data
        self.assertEqual(list(data["sessions"]), list(sessions))
        self.assertEqual(len(data["sessions"]), 1)
        self.assertEqual(list(data["sessions"])[0], SupportSessionSerializer(self.pending_session_support).data)

    def test_user_support_session_is_avaliable(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)

        data = response.json()
        self.assertIn("user_type", data)
        self.assertEqual(data["user_type"], "user")
        self.assertIn("ok", data)
        self.assertTrue(data["ok"])
        self.assertIn("support_session_id", data)
        self.assertEqual(data["support_session_id"], 2)
        self.assertIn("messages", data)
        messages = SupportMessageSerializer(
            SupportMessage.objects.filter(session=self.pending_session_support),
            many=True,
        ).data
        self.assertEqual(len(data["messages"]), len(messages))

    def test_user_support_session_is_not_avaliable(self):
        self.pending_session_support.status = SupportSession.Status.CLOSED
        self.pending_session_support.session_date = timezone.now() - timedelta(days=3)
        self.pending_session_support.save()

        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)

        data = response.json()
        self.assertIn("user_type", data)
        self.assertEqual(data["user_type"], "user")
        self.assertIn("ok", data)
        self.assertTrue(data["ok"])
        self.assertIn("support_session_id", data)
        self.assertNotEqual(data["support_session_id"], self.pending_session_support.id)
        self.assertIn("messages", data)
        self.assertEqual(list(data["messages"]), [])

    def test_admin_support_sessions_list_is_empty(self):

        for support_session in SupportSession.objects.all():
            support_session.status = SupportSession.Status.CLOSED
            support_session.save()

        self.client.login(username="another_admin", password="testpass")
        response = self.client.get(self.url)

        data = response.json()
        self.assertIn("user_type", data)
        self.assertEqual(data["user_type"], "admin")
        self.assertIn("ok", data)
        self.assertTrue(data["ok"])
        self.assertIn("sessions", data)
        self.assertEqual(list(data["sessions"]), [])

    def test_for_anonymous_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse("account:login")
        expected_url = f"{login_url}?next={self.url}"
        self.assertRedirects(response, expected_url)


class GetSupportSessionForAdminTest(TestCase):
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
        cls.user_1 = baker.make(
            FilmBazUser,
            username="user_1",
            email="user_1@gmail.com",
            phone="09000000001",
        )
        cls.user_1.set_password("testpass")
        cls.user_1.save()

        cls.user_2 = baker.make(
            FilmBazUser,
            username="user_2",
            email="user_2@gmail.com",
            phone="09000000006",
        )
        cls.user_2.set_password("testpass")
        cls.user_2.save()

        cls.user_3 = baker.make(
            FilmBazUser,
            username="user_3",
            email="user_3@gmail.com",
            phone="09000000007",
        )
        cls.user_3.set_password("testpass")
        cls.user_3.save()

        cls.user_4 = baker.make(
            FilmBazUser,
            username="user_4",
            email="user_4@gmail.com",
            phone="09000000008",
        )
        cls.user_4.set_password("testpass")
        cls.user_4.save()

        cls.user_5 = baker.make(
            FilmBazUser,
            username="user_5",
            email="user_5@gmail.com",
            phone="09000000009",
        )
        cls.user_5.set_password("testpass")
        cls.user_5.save()

        cls.only_superuser = baker.make(
            FilmBazUser,
            username="only_superuser",
            email="only_superuser@gmail.com",
            phone="09000000002",
        )
        cls.only_superuser.set_password("testpass")
        cls.only_superuser.is_superuser = True
        cls.only_superuser.save()

        cls.only_staff = baker.make(
            FilmBazUser,
            username="only_staff",
            email="only_staff@gmail.com",
            phone="09000000003",
        )
        cls.only_staff.set_password("testpass")
        cls.only_staff.is_staff = True
        cls.only_staff.save()

        cls.admin_1 = baker.make(
            FilmBazUser,
            username="admin_1",
            email="admin_1@gmail.com",
            phone="09000000004",
        )
        cls.admin_1.set_password("testpass")
        cls.admin_1.is_staff = True
        cls.admin_1.is_superuser = True
        cls.admin_1.save()

        cls.admin_2 = baker.make(
            FilmBazUser,
            username="admin_2",
            email="admin_2@gmail.com",
            phone="09000000005",
        )
        cls.admin_2.set_password("testpass")
        cls.admin_2.is_staff = True
        cls.admin_2.is_superuser = True
        cls.admin_2.save()

        cls.session_pending_unassigned = baker.make(
            SupportSession,
            id=1,
            user=cls.user_1,
            supporter=None,
            status=SupportSession.Status.PENDING,
        )

        cls.session_open_unassigned = baker.make(
            SupportSession,
            id=2,
            user=cls.user_2,
            supporter=None,
            status=SupportSession.Status.OPEN,
        )

        cls.session_open_assigned_admin1 = baker.make(
            SupportSession,
            id=3,
            user=cls.user_3,
            supporter=cls.admin_1,
            status=SupportSession.Status.OPEN,
        )

        cls.session_open_assigned_admin2 = baker.make(
            SupportSession,
            id=4,
            user=cls.user_4,
            supporter=cls.admin_2,
            status=SupportSession.Status.OPEN,
        )

        with freeze_time(timezone.now() - timedelta(days=1)):
            cls.session_closed_unassigned = baker.make(
                SupportSession,
                id=5,
                user=cls.user_1,
                supporter=None,
                status=SupportSession.Status.CLOSED,
            )

        with freeze_time(timezone.now() - timedelta(days=1)):
            cls.session_closed_assigned_admin1 = baker.make(
                SupportSession,
                id=6,
                user=cls.user_2,
                supporter=cls.admin_1,
                status=SupportSession.Status.CLOSED,
            )

        cls.session_for_race_claim = baker.make(
            SupportSession,
            id=7,
            user=cls.user_5,
            supporter=None,
            status=SupportSession.Status.PENDING,
        )

        for i in range(1, 4):
            with freeze_time(timezone.now() + timedelta(hours=i)):
                baker.make(
                    SupportMessage,
                    is_seen=True if i > 2 else False,
                    text=f"message {i}",
                    session=cls.session_pending_unassigned,
                    sender=cls.user_1,
                )

        for i in range(1, 6):
            with freeze_time(timezone.now() + timedelta(hours=i)):
                baker.make(
                    SupportMessage,
                    is_seen=False,
                    text=f"message {i}",
                    session=cls.session_open_assigned_admin2,
                    sender=cls.user_4,
                )
        for i in range(1, 3):
            with freeze_time(timezone.now() + timedelta(hours=i)):
                baker.make(
                    SupportMessage,
                    is_seen=False,
                    text=f"race msg {i}",
                    session=cls.session_for_race_claim,
                    sender=cls.user_5,
                )

    def setUp(self):
        self.client = Client()

    def test_get_sessions_anonymous_user(self):
        url = reverse("support:get_support_session_for_admin", args=[self.session_pending_unassigned.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse("account:login")
        expected_url = f"{login_url}?next={url}"
        self.assertRedirects(response, expected_url)

    def test_get_sessions_simple_user(self):
        url = reverse("support:get_support_session_for_admin", args=[self.session_pending_unassigned.id])
        self.client.login(username=self.user_1.username, password="testpass")
        response = self.client.get(url)

        data = response.json()
        self.assertIn("ok", data)
        self.assertFalse(data["ok"])

    def test_get_sessions_staff_only(self):
        url = reverse("support:get_support_session_for_admin", args=[self.session_pending_unassigned.id])

        self.client.login(username=self.only_staff.username, password="testpass")
        response = self.client.get(url)

        data = response.json()
        self.assertIn("ok", data)
        self.assertFalse(data["ok"])

    def test_get_sessions_superuser_only(self):
        url = reverse("support:get_support_session_for_admin", args=[self.session_pending_unassigned.id])

        self.client.login(username=self.only_superuser.username, password="testpass")
        response = self.client.get(url)

        data = response.json()
        self.assertIn("ok", data)
        self.assertFalse(data["ok"])

    def test_get_sessions_session_id_not_found(self):
        url = reverse("support:get_support_session_for_admin", args=[999])

        self.client.login(username=self.only_superuser.username, password="testpass")
        response = self.client.get(url)

        data = response.json()
        self.assertIn("ok", data)
        self.assertFalse(data["ok"])

    def test_get_sissions_session_is_closed(self):
        url = reverse("support:get_support_session_for_admin", args=[self.session_closed_unassigned.id])
        self.client.login(username=self.admin_1.username, password="testpass")
        response = self.client.get(url)

        data = response.json()
        self.assertIn("ok", data)
        self.assertFalse(data["ok"])

    def test_get_sissions_session_is_pending(self):
        url = reverse("support:get_support_session_for_admin", args=[self.session_pending_unassigned.id])
        self.client.login(username=self.admin_1.username, password="testpass")
        response = self.client.get(url)

        data = response.json()
        self.assertIn("ok", data)
        self.assertTrue(data["ok"])
        self.assertIn("user_type", data)
        self.assertIn("support_session_id", data)
        self.assertIn("messages", data)

        self.assertEqual(data["user_type"], "admin")
        self.assertEqual(data["support_session_id"], self.session_pending_unassigned.id)

        messages = SupportMessageSerializer(self.session_pending_unassigned.messages.all(), many=True).data
        self.assertEqual(len(data["messages"]), len(messages))


    def test_get_sissions_session_is_open(self):
        url = reverse("support:get_support_session_for_admin", args=[self.session_open_unassigned.id])
        self.client.login(username=self.admin_1.username, password="testpass")
        response = self.client.get(url)

        data = response.json()
        self.assertIn("ok", data)
        self.assertTrue(data["ok"])
        self.assertIn("user_type", data)
        self.assertIn("support_session_id", data)
        self.assertIn("messages", data)

        self.assertEqual(data["user_type"], "admin")
        self.assertEqual(data["support_session_id"], self.session_open_unassigned.id)

        self.assertEqual(list(data["messages"]), [])