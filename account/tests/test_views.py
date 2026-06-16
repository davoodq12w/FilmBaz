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


class EditUserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = FilmBazUser.objects.create_user(
            username="test",
            email="test@gmail.com",
            phone="09112223344",
            password="testpass"
        )
        cls.other_user = FilmBazUser.objects.create_user(
            username="hacker",
            email="hacker@gmail.com",
            phone="09112223355",
            password="hackerpass"
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("account:edit_user")

    def test_redirect_for_anonymous_user(self):
        response = self.client.get(self.url)
        login_url = reverse("account:login")
        expected_url = f"{login_url}?next={self.url}"

        self.assertRedirects(response, expected_url)

    def test_edit_user_view_get(self):
        self.client.login(username="test", password="testpass")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/edit_user.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["username"], self.user.username)

    def test_edit_user_view_post_success(self):
        self.client.login(username="test", password="testpass")
        new_data = {
            "username": "new_name",
            "email": "new_name@gmail.com",
            "phone": "09001112233",
        }

        response = self.client.post(self.url, data=new_data)

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()

        self.assertEqual(self.user.username, "new_name")
        self.assertEqual(self.user.email, "new_name@gmail.com")
        self.assertEqual(self.user.phone, "09001112233")

    def test_edit_user_view_post_invalid(self):
        self.client.login(username="test", password="testpass")

        invalid_data = {
            "username": "test@#",  # غیرمجاز طبق Regex فرم
            "email": "invalid-email",
            "phone": "123"
        }

        response = self.client.post(self.url, data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "username",
            "نام کاربری باید از اعداد و حروف انگلیسی و _ تشکیل شده باشد",
        )
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, "test@#")

    def test_edit_user_view_only_self_update(self):
        self.client.login(username="hacker", password="hackerpass")

        new_data = {
            "username": "hacker_new",
            "email": "hacker_new@gmail.com",
            "phone": "09001112266"
        }

        self.client.post(self.url, data=new_data)
        original_davood = FilmBazUser.objects.get(username="test")
        self.assertEqual(original_davood.phone, "09112223344")
