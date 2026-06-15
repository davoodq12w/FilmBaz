from django.test import TestCase
from account.models import FilmBazUser


class FilmBazUserModelTests(TestCase):

    def test_str_method(self):
        user = FilmBazUser.objects.create_user(
            username="test",
            password="test_password",
            phone="09112223344",
            email="test@gmail.com",
        )
        self.assertEqual(str(user), "test")

    def test_create_super_user_method(self):
        super_user = FilmBazUser.objects.create_superuser(
            username="superuser",
            password="test_password",
            phone="09112223355",
            email="superuser@gmail.com",
        )
        self.assertEqual(super_user.is_staff, True)
        self.assertEqual(super_user.is_superuser, True)
