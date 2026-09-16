from django.urls import path
from . import views

app_name = 'film_api'

urlpatterns = [
    path('home/', views.HomePageApi.as_view(), name='home_page'),
    path("movies/", views.MovieListApi.as_view(), name='movie_list'),
    path("genres/", views.GenreListApi.as_view(), name='genre_list'),
    path("movies/years/", views.YearListApi.as_view(), name='movie_year_list'),
    path("movies/<int:pk>/<slug:slug>/", views.MovieDetailApi.as_view(), name='movie_detail'),
    path("movies/add_comment/", views.AddCommentApi.as_view(), name='add_comment'),
    path("movies/search/", views.SearchApi.as_view(), name='search_movie'),
    path("movies/save/", views.SaveMovieApi.as_view(), name='save_movie'),
    path("movies/like/", views.LikeMovieApi.as_view(), name='like_movie'),
    path("movies/episodes/<int:pk>/", views.WatchMovieApi.as_view(), name='watch_movie'),
    path("movies/episdoes/progress/", views.WatchProgressApi.as_view(), name="watch_progress")
]
