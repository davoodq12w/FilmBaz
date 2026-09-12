from django.urls import path
from . import views

app_name = 'film_api'

urlpatterns = [
    path('home/', views.HomePageApi.as_view(), name='home_page'),
    path("movies/", views.MovieListApi.as_view(), name='movie_list'),
    path("genres/", views.GenreListApi.as_view(), name='genre_list'),
    path("movies/years/", views.YearListApi.as_view(), name='movie_year_list'),
]
