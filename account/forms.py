from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import FilmBazUser, Ticket
import re
from django.contrib.auth.forms import AuthenticationForm


class FilmBazUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = FilmBazUser
        fields = "__all__"


class FilmBazUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = FilmBazUser
        fields = "__all__"


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "نام کاربری"
        self.fields["password"].label = "رمز"

    def clean_username(self):
        username = self.cleaned_data.get("username")
        is_valid = re.findall(r"^\w+$", username)

        if not is_valid:
            raise forms.ValidationError("نام کاربری باید از اعداد و حروف و _ تشکیل شده باشد!")

        if not FilmBazUser.objects.filter(username=username).exists():
            raise forms.ValidationError("نام کاربری وجود ندارد!")
        return username


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(label="رمز")
    password2 = forms.CharField(label=" تکرار رمز")

    class Meta:
        model = FilmBazUser
        fields = ["username", "phone", "email"]
        labels = {
            "username": "نام کاربری",
            "phone": "شماره تلفن",
            "email": "ایمیل",
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        is_valid = re.findall(r"^\w+$", username)

        if not is_valid:
            raise forms.ValidationError("نام کاربری باید از اعداد و حروف و _ تشکیل شده باشد")

        if FilmBazUser.objects.filter(username=username).exists():
            raise forms.ValidationError("نام کاربری از قبل وجود دارد")

        return username

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if not password == password2:
            raise forms.ValidationError("رمز ها باهم یکسان نیستند!")
        return password

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if self.instance.pk:
            if FilmBazUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('شماره تلفن درحال حاضر موجود میباشد')
        else:
            if FilmBazUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('شماره تلفن درحال حاضر موجود میباشد')

        if not phone.isdigit():
            raise forms.ValidationError('شماره تلفن باید فقط عدد باشد')

        if len(phone) != 11:
            raise forms.ValidationError('تعداد ارقام باید 11 رقم باشد')

        if not phone.startswith('09'):
            raise forms.ValidationError('شماره تلفن باید با 09 شروع شود')

        return phone

    def clean_email(self):

        email = self.cleaned_data.get("email")
        is_valid = re.findall(r"^(?:[\w.]+@)(?:\w+)\.(?:[a-zA-z]{2,3})$", email)

        if not is_valid:
            raise forms.ValidationError("ایمیل درست نوشته نشده است")

        if FilmBazUser.objects.filter(email=email).exists():
            raise forms.ValidationError("ایمیل از قبل وجود دارد")

        return email


class EditUserForm(forms.ModelForm):
    class Meta:
        model = FilmBazUser
        fields = ["image", "username", "phone", "email"]
        labels = {
            "username": "نام کاربری",
            "phone": "شماره تلفن",
            "email": "ایمیل",
            "image": "",
        }
        widgets = {
            "image": forms.FileInput(attrs={"class": "edit-user-image"})
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        is_valid = re.findall(r"^\w+$", username)

        if not is_valid:
            raise forms.ValidationError("نام کاربری باید از اعداد و حروف و _ تشکیل شده باشد")

        if FilmBazUser.objects.filter(username=username).exclude(id=self.instance.pk).exists():
            raise forms.ValidationError("نام کاربری از قبل وجود دارد")

        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if self.instance.pk:
            if FilmBazUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('شماره تلفن درحال حاضر موجود میباشد')
        else:
            if FilmBazUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('شماره تلفن درحال حاضر موجود میباشد')

        if not phone.isdigit():
            raise forms.ValidationError('شماره تلفن باید فقط عدد باشد')

        if len(phone) != 11:
            raise forms.ValidationError('تعداد ارقام باید 11 رقم باشد')

        if not phone.startswith('09'):
            raise forms.ValidationError('شماره تلفن باید با 09 شروع شود')

        return phone

    def clean_email(self):

        email = self.cleaned_data.get("email")
        is_valid = re.findall(r"^(?:[\w.]+@)(?:\w+)\.(?:[a-zA-Z]{2,3})$", email)

        if not is_valid:
            raise forms.ValidationError("ایمیل درست نوشته نشده است")

        if FilmBazUser.objects.filter(email=email).exclude(id=self.instance.pk).exists():
            raise forms.ValidationError("ایمیل از قبل وجود دارد")

        return email


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "text",]
