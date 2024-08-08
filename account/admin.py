from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import FilmBazUserChangeForm, FilmBazUserCreationForm


# Register your models here.


@admin.register(FilmBazUser)
class FilmBazUserAdmin(UserAdmin):
    ordering = ['username']
    add_form = FilmBazUserCreationForm
    form = FilmBazUserChangeForm
    model = FilmBazUser
    list_display = ['username', 'phone', 'email', 'created', 'is_active']
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("phone", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Date Datas", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {"fields": ("username", "password1", "password2")}),
        ("Personal Info", {"fields": ("phone", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Date Datas", {"fields": ("last_login",)}),
    )
