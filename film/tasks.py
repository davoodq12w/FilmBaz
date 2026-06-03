from celery import shared_task
import requests
from decouple import config
from .models import Movie
from django.utils.text import slugify
from django.core.files.base import ContentFile

tmdb_token = config("TMDB_TOKEN")


@shared_task(queue="api")
def tmdb_movie_list(
        genre=None,
        cast=None,
        crew=None,
        vote_average_gte=None,
        page=1,
        language="en-US",
        adult=False,
        country=None,
):
    url = "https://api.themoviedb.org/3/discover/movie"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_token}",
    }

    params = {
        "with_genres": genre,
        "with_cast": cast,
        "with_crew": crew,
        "vote_average.gte": vote_average_gte,
        "language": language,
        "page": page,
        "include_adult": adult,
        "with_origin_country": country,

    }

    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()
    save_new_movies.delay(data)

    return data


@shared_task(queue="default")
def save_new_movies(response: dict):
    movies = response["results"]
    for movie in movies:
        data = {
            "poster_path": movie["poster_path"],
            "backdrop_path": movie["backdrop_path"],
            "title": movie["title"],
            "slug": slugify(movie["title"]),
            "description": movie["overview"],
            "popularity": movie["popularity"],
            "release_date": movie.get("release_date") or None,
            "adult": movie["adult"],
        }
        movie_obj, created = Movie.objects.update_or_create(tmdb_id=movie["id"], defaults=data)

        if not movie_obj.images_downloaded:
            download_movie_images.delay(movie_obj.id)


@shared_task(queue="download",
             autoretry_for=(requests.RequestException,),
             retry_backoff=True,
             max_retries=5)
def download_movie_images(movie_obj_id: int):
    movie = Movie.objects.get(id=movie_obj_id)

    if movie.images_downloaded:
        return

    poster_downloaded = False
    backdrop_downloaded = False

    if movie.poster_path:
        poster_url = (
            f"https://image.tmdb.org/t/p/original"
            f"{movie.poster_path}"
        )

        response = requests.get(poster_url, timeout=30)
        response.raise_for_status()

        movie.poster.save(
            f"poster_{movie.tmdb_id}.jpg",
            ContentFile(response.content),
            save=False,
        )
        poster_downloaded = True

    if movie.backdrop_path:
        backdrop_url = (
            f"https://image.tmdb.org/t/p/original"
            f"{movie.backdrop_path}"
        )

        response = requests.get(backdrop_url, timeout=30)
        response.raise_for_status()

        movie.backdrop.save(
            f"backdrop_{movie.tmdb_id}.jpg",
            ContentFile(response.content),
            save=False,
        )
        backdrop_downloaded = True

    movie.images_downloaded = (
            (not movie.poster_path or poster_downloaded)
            and
            (not movie.backdrop_path or backdrop_downloaded)
    )

    movie.save()
