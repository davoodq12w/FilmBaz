from django.urls import path
from . import views

app_name = "account_api"

urlpatterns = [
    path("login/", views.UserLoginAPI.as_view(), name="login"),
    path("logout/", views.UserLogoutAPI.as_view(), name="logout"),
    path("token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("create_user/", views.CreateUserApi.as_view(), name="create_user"),
]
