from django.urls import path
from . import views

app_name = "account_api"

urlpatterns = [
    path("login/", views.UserLoginApi.as_view(), name="login"),
    path("logout/", views.UserLogoutApi.as_view(), name="logout"),
    path("token/refresh/", views.CustomTokenRefreshApi.as_view(), name="token_refresh"),
    path("create_user/", views.CreateUserApi.as_view(), name="create_user"),
    path("user/", views.UserDetailApi.as_view(), name="user_detail"),
    path("user/genres/", views.UserGenresApi.as_view(), name="user_favorite_genres"),
    path("ticket/", views.TicketApi.as_view(), name="ticket"),
    path("user/saves/", views.UserSavesApi.as_view(), name="user_saves"),
    path("user/likes/", views.UserLikesApi.as_view(), name="user_likes"),
    path("reset_password/", views.ResetPasswordApi.as_view(), name="reset_password"),
    path("reset_password/confirm/", views.ConfirmResetPasswordApi.as_view(), name="confirm_reset_password"),
    path("change_password/", views.ChangePasswordApi.as_view(), name="change_password"),

]
