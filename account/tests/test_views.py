from django.test import TestCase, Client
from django.urls import reverse
from account.models import FilmBazUser, Ticket
from model_bakery import baker
from unittest.mock import patch
from film.models import Movie


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


class TicketViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(
            FilmBazUser,
            username="test",
            phone="09112223344",
            email="test@gmail.com"
        )
        cls.user.set_password("testpass")
        cls.user.save()

    def setUp(self):
        self.client = Client()
        self.url = reverse("account:ticket")

    def test_redirect_for_anonymous_user(self):
        response = self.client.get(self.url)
        login_url = reverse("account:login")
        expected_url = f"{login_url}?next={self.url}"

        self.assertRedirects(response, expected_url)

    def test_ticket_get_method(self):
        self.client.login(username="test", password="testpass")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account:profile"))

    def test_ticket_not_ellowed_methods(self):
        self.client.login(username="test", password="testpass")
        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/not_allowed.html")

    @patch("account.views.send_confirm_email.delay")
    def test_create_ticket(self, mock_send_email):
        self.client.login(username="test", password="testpass")
        data = {
            "subject": Ticket.Subject.CRITICISM,
            "text": "test"
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.subject, data["subject"])
        self.assertEqual(ticket.text, data["text"])
        self.assertEqual(ticket.email, self.user.email)
        self.assertEqual(ticket.phone, self.user.phone)
        self.assertRedirects(response, reverse("account:profile"))
        mock_send_email.assert_called_once()

    def test_anonymous_user_cannot_create_ticket(self):
        data = {
            "subject": Ticket.Subject.CRITICISM,
            "text": "test"
        }

        response = self.client.post(self.url, data=data)

        login_url = reverse("account:login")
        expected_url = f"{login_url}?next={self.url}"

        self.assertEqual(Ticket.objects.count(), 0)
        self.assertRedirects(response, expected_url)

    def test_invalid_ticket_form_does_not_create_ticket(self):
        self.client.login(username="test", password="testpass")

        data = {
            "subject": Ticket.Subject.CRITICISM,
            "text": ""
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ticket.objects.count(), 0)


class UserSavesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = baker.make(
            FilmBazUser,
            username="test1",
            phone="09112223344",
            email="test1@gmail.com"
        )
        cls.user1.set_password("testpass")
        cls.user1.save()
        cls.user2 = baker.make(
            FilmBazUser,
            username="test2",
            phone="09112223355",
            email="test2@gmail.com"
        )
        cls.user2.set_password("testpass")
        cls.user2.save()

        cls.movie1 = baker.make(
            Movie,
            fa_title="بتمن",
            orj_title="Batman",
            slug="batman",
        )
        cls.movie2 = baker.make(
            Movie,
            fa_title="جوکر",
            orj_title="Joker",
            slug="joker",
        )
        cls.movie1.users_saved.add(cls.user1)
        cls.movie1.save()
        cls.movie2.users_saved.add(cls.user2)
        cls.movie2.save()

    def setUp(self):
        self.client = Client()
        self.url = reverse("account:saves")

    def test_redirect_for_anonymous_user(self):
        response = self.client.get(self.url)
        login_url = reverse("account:login")
        expected_url = f"{login_url}?next={self.url}"
        self.assertRedirects(response, expected_url)

    def test_get_list_of_movies(self):
        self.client.login(username="test1", password="testpass")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 1)
        self.assertEqual(response.context["movies"][0], self.movie1)
        self.assertNotEqual(response.context["movies"][0], self.movie2)
