from django.test import TestCase
from support.models import SupportSession, SupportMessage
from account.models import FilmBazUser
from model_bakery import baker
from django.db import IntegrityError, transaction


class SupportSessionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(FilmBazUser, username="user")
        cls.supporter = baker.make(FilmBazUser, username="supporter")

        cls.supportsession1 = SupportSession.objects.create(
            user=cls.user,
            supporter=cls.supporter
        )
        cls.supportsession2 = SupportSession.objects.create()

    def test_str_method(self):
        self.assertEqual(
            str(self.supportsession1),
            "SupportSession:user"
        )
        self.assertEqual(
            str(self.supportsession2),
            "SupportSession:NoUser"
        )

    def test_unique_sessions_per_day(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SupportSession.objects.create(
                    user=self.user,
                )

        another_user = baker.make(FilmBazUser, username="another_user")

        session = SupportSession.objects.create(
            user=another_user,
        )

        self.assertEqual(session.user, another_user)
