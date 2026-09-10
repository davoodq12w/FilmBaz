from django.urls import path
from . import views

app_name = "analytics_api"

urlpatterns = [
    path("share/", v),
]
