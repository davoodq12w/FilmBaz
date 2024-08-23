from django.urls import path
from . import views

app_name = "film"

urlpatterns = [
    path('', views.MoviesList.as_view(), name="movies_list"),
    path("movies/<int:pk>/<slug:slug>", views.MovieDetail.as_view(), name="movies_detail"),
    path("movies/add-comment", views.CommentView.as_view(), name="add_comment"),
    path("movies/search", views.SearchMovie.as_view(), name="search"),
    path("save_movie/", views.SaveMovieView.as_view(), name="save_movie"),
]
