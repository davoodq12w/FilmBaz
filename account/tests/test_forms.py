from django.conf.urls.static import static
from django.test import TestCase, Client
from ..models import FilmBazUser
from account.forms import CreateUserForm, EditUserForm


class TestCreateUserForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        FilmBazUser.objects.create(username="davood_q12w", password="davodrashi13811212", phone="09037246850",
                                   email="davod.q12w@gmail.com")

    def setUp(self):
        self.data = {"username": "davood",
                     "password": "davodrashi13811212",
                     "password2": "davodrashi13811212",
                     "email": "davood@gmail.com",
                     "phone": "09999999999", }

    def test_user_is_valid(self):
        form = CreateUserForm(data=self.data)

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_username_is_not_valid(self):
        data = self.data
        data["username"] = "davood.%$"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("نام کاربری باید از اعداد و حروف و _ تشکیل شده باشد", form.errors["username"])

    def test_username_is_exists(self):
        data = self.data
        data["username"] = "davood_q12w"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("نام کاربری از قبل وجود دارد", form.errors["username"])

    def test_password_not_match(self):
        data = self.data
        data["password2"] = "davood"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("رمز ها باهم یکسان نیستند!", form.errors["password2"])

    def test_phone_is_exists(self):
        data = self.data
        data["phone"] = "09037246850"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('شماره تلفن درحال حاضر موجود میباشد', form.errors["phone"])

    def test_phone_is_not_digit(self):
        data = self.data
        data["phone"] = "0903724685a"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('شماره تلفن باید فقط عدد باشد', form.errors["phone"])

    def test_phone_is_not_11_digits(self):
        # when phone is 10 digits
        data = self.data
        data['phone'] = "0999999999"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('تعداد ارقام باید 11 رقم باشد', form.errors["phone"])

        # when phone is 12 digits

        data = self.data
        data['phone'] = "099999999999"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('Ensure this value has at most 11 characters (it has 12).', form.errors["phone"])

    def test_phone_not_starts_with_09(self):
        data = self.data
        data['phone'] = "99999999999"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('شماره تلفن باید با 09 شروع شود', form.errors["phone"])

    def test_email_is_not_valid(self):
        emails = [
            "davood@gmail.comm",
            "davo@d$gmail.com",
            "davood@gma$l.com",
            "davood@gmail.i",
            "davood@gmail.com.ir",
        ]
        data = self.data
        for email in emails:
            data['email'] = str(email)
            form = CreateUserForm(data=data)

            self.assertFalse(form.is_valid())
            self.assertIn("ایمیل درست نوشته نشده است", form.errors["email"])

    def test_email_is_exists(self):
        data = self.data
        data["email"] = "davod.q12w@gmail.com"
        form = CreateUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("ایمیل از قبل وجود دارد", form.errors["email"])


class TestEditUserForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        FilmBazUser.objects.create(username="user", email="user@gmail.com",
                                   password="user12341234", phone="09123456789")

    def setUp(self):
        self.user = FilmBazUser.objects.create(username="davoodq12w", phone="09037246850",
                                          email="davod.q12w@gmail.com", password="davodrashi13811212")
        self.data = {
            "username": "not_davood",
            "email": "not_davood@gmail.com",
            "phone": "09000000000",
            "image": None,
        }

    def test_edit_user_is_valid(self):
        form = EditUserForm(instance=self.user, data=self.data)

        self.assertEqual(len(form.errors), 0)
        self.assertTrue(form.is_valid())

    def test_username_is_not_valid(self):
        data = self.data
        data["username"] = "not_davood@#"

        form = EditUserForm(instance=self.user, data=data)

        self.assertIn("نام کاربری باید از اعداد و حروف و _ تشکیل شده باشد", form.errors["username"])
        self.assertFalse(form.is_valid())

    def test_username_is_exists(self):
        data = self.data
        data["username"] = "user"

        form = EditUserForm(instance=self.user, data=data)

        self.assertIn("نام کاربری از قبل وجود دارد", form.errors["username"])
        self.assertFalse(form.is_valid())

    def test_username_is_for_myself(self):
        data = self.data
        data["username"] = "davoodq12w"

        form = EditUserForm(instance=self.user, data=data)

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_phone_is_exists(self):
        data = self.data
        data["phone"] = "09123456789"

        form = EditUserForm(instance=self.user, data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("شماره تلفن درحال حاضر موجود میباشد", form.errors["phone"])

    def test_phone_is_for_myself(self):
        data = self.data
        data["phone"] = "09037246850"

        form = EditUserForm(instance=self.user, data=data)

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_phone_is_not_digit(self):
        data = self.data
        data["phone"] = "0903624685u"

        form = EditUserForm(instance=self.user, data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("شماره تلفن باید فقط عدد باشد", form.errors["phone"])

    def test_phone_is_not_11_digits(self):
        # when phone is 10 digits
        data = self.data
        data['phone'] = "0999999999"
        form = EditUserForm(instance=self.user, data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('تعداد ارقام باید 11 رقم باشد', form.errors["phone"])

        # when phone is 12 digits

        data = self.data
        data['phone'] = "099999999999"
        form = EditUserForm(instance=self.user, data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('Ensure this value has at most 11 characters (it has 12).', form.errors["phone"])

    def test_phone_not_starts_with_09(self):
        data = self.data
        data['phone'] = "99999999999"
        form = EditUserForm(instance=self.user, data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('شماره تلفن باید با 09 شروع شود', form.errors["phone"])

    def test_email_is_not_valid(self):
        emails = [
            "davood@gmail.comm",
            "davo@d$gmail.com",
            "davood@gma$l.com",
            "davood@gmail.i",
            "davood@gmail.com.ir",

        ]
        data = self.data
        for email in emails:
            data['email'] = str(email)
            form = EditUserForm(instance=self.user, data=data)

            self.assertFalse(form.is_valid())
            self.assertIn("ایمیل درست نوشته نشده است", form.errors["email"])

    def test_email_is_exists(self):
        data = self.data
        data["email"] = 'user@gmail.com'

        form = EditUserForm(instance=self.user, data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("ایمیل از قبل وجود دارد", form.errors["email"])

    def test_email_is_for_myself(self):
        data = self.data
        data["email"] = "davod.q12w@gmail.com"

        form = EditUserForm(instance=self.user, data=data)

        self.assertTrue(form.is_valid)
        self.assertEqual(len(form.errors), 0)
