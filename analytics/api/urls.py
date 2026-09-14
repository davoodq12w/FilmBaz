from django.urls import path
from . import views

app_name = "analytics_api"

urlpatterns = [
    path("intraction/", views.IntractionApi.as_view(), name="share_intraction"),
]
