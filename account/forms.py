from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import FilmBazUser


class FilmBazUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = FilmBazUser
        fields = "__all__"


class FilmBazUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = FilmBazUser
        fields = "__all__"
