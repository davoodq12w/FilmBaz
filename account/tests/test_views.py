from django.test import TestCase, Client
from django.urls import reverse
from account.models import FilmBazUser
from model_bakery import baker


class CreateUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("account:create_user")
        self.redirect_url = reverse("film:home_page")

    def test_create_user_method(self):
        data = {
            "username": "test",
            "phone": "09112223344",
            "email": "test@gmail.com",
            "password": "testpass",
            "password2": "testpass",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(FilmBazUser.objects.count(), 1)

        user = FilmBazUser.objects.first()
        self.assertEqual(user.username, "test")
        self.assertEqual(user.phone, "09112223344")
        self.assertEqual(user.email, "test@gmail.com")

        self.assertTrue(user.check_password("testpass"))
        self.assertRedirects(response, self.redirect_url)


class UserProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(
            FilmBazUser,
            username="test",
            phone="09112223344",
            email="test@gmail.com",
        )
        cls.user.set_password("testpass")
        cls.user.save()

    def setUp(self):
        self.client = Client()
        self.url = reverse("account:profile")

    def test_redirect_for_anonymous_user(self):
        response = self.client.get(self.url)
        login_url = reverse("account:login")
        expected_url = f"{login_url}?next={self.url}"

        self.assertRedirects(response, expected_url)

    def test_get_profile(self):
        self.client.login(username="test", password="testpass")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/profile.html")
        self.assertEqual(response.context['user'], self.user)

    def test_method_not_allowed(self):
        self.client.login(username="test", password="testpass")
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/not_allowed.html")
