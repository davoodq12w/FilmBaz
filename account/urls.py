from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = "account"

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name="login"),
    path('logout/', views.UserLogout.as_view(), name="logout"),
    path('create_user/', views.CreateUser.as_view(), name="create_user"),
    path('profile/<int:pk>/<slug:username>', views.UserProfile.as_view(), name="profile"),
    path("edit_usr/<int:pk>/<slug:username>", views.EditUser.as_view(), name="edit_user"),
    # =====================================
    # for password reset
    # =====================================
    path('password-reset/',
         auth_views.PasswordResetView.as_view(success_url=reverse_lazy("account:password_reset_done")),
         name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy("account:password_reset_complete")),
         name="password_reset_confirm"),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # =====================================
    # for password change
    # =====================================
    path('password-change/', auth_views.PasswordChangeView.as_view(success_url='done'), name="password_change"),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
]
