from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name="login"),
    path('logout/', views.UserLogout.as_view(), name="logout"),
    path('create_user/', views.CreateUser.as_view(), name="create_user"),
    path('profile/<int:pk>/<slug:username>', views.UserProfile.as_view(), name="profile"),
    path("edit_usr/<int:pk>/<slug:username>", views.EditUser.as_view(), name="edit_user"),
]
