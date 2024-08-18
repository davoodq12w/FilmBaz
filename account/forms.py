from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import FilmBazUser
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
            "phone":  "شماره تلفن",
            "email": "ایمیل",
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if not password == password2:
            raise forms.ValidationError("رمز ها باهم یکسان نیستند!")
        return password
