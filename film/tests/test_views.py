from django.test import TestCase, Client, override_settings
from model_bakery import baker
from film.models import Movie, Genre
from datetime import timedelta, date
from django.utils import timezone
from django.shortcuts import reverse
from django.http import JsonResponse
from unittest.mock import patch
from django.core.cache import cache
import hashlib
from film.views import MoviesList
from django.core.paginator import Page, Paginator


class HomePageViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.movie1 = baker.make(
            Movie,
            fa_title="بتمن",
            orj_title="Batman",
            slug="batman",
            release_date=timezone.now(),
            rate=5.0,
        )

        cls.movie2 = baker.make(
            Movie,
            fa_title="جوکر",
            orj_title="Joker",
            slug="joker",
            release_date=timezone.now() - timedelta(days=1),
            rate=6.0,
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("film:home_page")

    def test_home_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "film/home_page.html")

    def test_home_page_context(self):
        response = self.client.get(self.url)

        self.assertIn("new_movies", response.context)
        self.assertIn("top_movies", response.context)

    def test_home_page_new_movies(self):
        response = self.client.get(self.url)

        new_movies = list(response.context["new_movies"])

        self.assertEqual(new_movies[0], self.movie1)
        self.assertEqual(new_movies[1], self.movie2)

    def test_home_page_top_movies(self):
        response = self.client.get(self.url)

        top_movies = list(response.context["top_movies"])

        self.assertEqual(top_movies[0], self.movie2)
        self.assertEqual(top_movies[1], self.movie1)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class MoviesListViewFiltersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre1 = baker.make(Genre, id=1, en_name="1")
        cls.genre2 = baker.make(Genre, id=2, en_name="2")
        cls.movie1 = baker.make(Movie, orj_title="1", genres=[cls.genre1], release_date=date(2020, 3, 3))
        cls.movie2 = baker.make(Movie, orj_title="2", genres=[cls.genre1], release_date=date(2020, 3, 3))
        cls.movie3 = baker.make(Movie, orj_title="3", adult=True, genres=[cls.genre1], release_date=date(2020, 3, 3))
        cls.movie4 = baker.make(Movie, orj_title="4", adult=True, genres=[cls.genre2], release_date=date(2021, 3, 3))
        cls.movie5 = baker.make(Movie, orj_title="5", adult=True, genres=[cls.genre2], release_date=date(2021, 3, 3))

    def setUp(self):
        self.client = Client()
        self.url = reverse("film:movies_list")

    def test_movies_no_filters(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 5)

    def test_movies_only_adults(self):
        response = self.client.get(f"{self.url}?adult=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 3)

    def test_movies_only_childrens(self):
        response = self.client.get(f"{self.url}?adult=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 2)

    def test_movies_invalid_adult(self):
        response = self.client.get(f"{self.url}?adult=invalid")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 5)

    def test_movies_with_genre(self):
        response = self.client.get(f"{self.url}?genre_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 3)

    def test_movies_with_out_of_range_genre_id(self):
        response = self.client.get(f"{self.url}?genre_id=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 0)

    def test_movies_with_invalid_genre(self):
        response = self.client.get(f"{self.url}?genre_id=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 5)

    def test_movies_with_release_date(self):
        response = self.client.get(f"{self.url}?release_date=2020")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 3)

    def test_moives_with_out_of_range_release_date(self):
        response = self.client.get(f"{self.url}?release_date=3020")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 0)

    def test_movies_with_invalid_release_date(self):
        response = self.client.get(f"{self.url}?release_date=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 5)

    def test_movies_with_multiple_filters(self):
        response = self.client.get(f"{self.url}?release_date=2020&genre_id=1&adult=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 1)

    def test_movies_with_multiple_filters_invalid_adult(self):
        response = self.client.get(f"{self.url}?release_date=2020&genre_id=1&adult=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 3)

    def test_movies_with_multiple_filters_invalid_genre_id(self):
        response = self.client.get(f"{self.url}?release_date=2020&genre_id=true&adult=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 1)

    def test_movies_with_multiple_filters_invalid_release_date(self):
        response = self.client.get(f"{self.url}?release_date=false&genre_id=1&adult=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 1)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class MoviesListViewOrderingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie1 = baker.make(Movie, orj_title="1", release_date=date(2019, 3, 3), rate=5.0)
        cls.movie2 = baker.make(Movie, orj_title="2", release_date=date(2018, 3, 3), rate=6.0)
        cls.movie3 = baker.make(Movie, orj_title="3", release_date=date(2017, 3, 3), rate=7.0)
        cls.movie4 = baker.make(Movie, orj_title="4", release_date=date(2016, 3, 3), rate=8.0)
        cls.movie5 = baker.make(Movie, orj_title="5", release_date=date(2015, 3, 3), rate=9.0)

    def setUp(self):
        self.client = Client()
        self.url = reverse("film:movies_list")

    def test_movies_order_by_oldest(self):
        response = self.client.get(f"{self.url}?ordering=release_date")
        self.assertEqual(response.status_code, 200)
        movies = response.context["movies"]

        self.assertEqual(movies[0].orj_title, "5")
        self.assertEqual(movies[-1].orj_title, "1")

    def test_movies_order_by_latest(self):
        response = self.client.get(f"{self.url}?ordering=-release_date")
        self.assertEqual(response.status_code, 200)
        movies = response.context["movies"]

        self.assertEqual(movies[0].orj_title, "1")
        self.assertEqual(movies[-1].orj_title, "5")

    def test_movies_order_by_most_rated(self):
        response = self.client.get(f"{self.url}?ordering=-rate")
        self.assertEqual(response.status_code, 200)
        movies = response.context["movies"]

        self.assertEqual(movies[0].orj_title, "5")
        self.assertEqual(movies[-1].orj_title, "1")

    def test_movies_order_by_less_rated(self):
        response = self.client.get(f"{self.url}?ordering=rate")
        self.assertEqual(response.status_code, 200)
        movies = response.context["movies"]

        self.assertEqual(movies[0].orj_title, "1")
        self.assertEqual(movies[-1].orj_title, "5")

    def test_movies_invalid_ordering(self):
        response = self.client.get(f"{self.url}?ordering=true")
        self.assertEqual(response.status_code, 200)
        movies = response.context["movies"]

        self.assertEqual(movies[0].orj_title, "1")
        self.assertEqual(movies[-1].orj_title, "5")


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class MoviesListViewPaginationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movies = []
        for i in range(1, 26):
            movie = baker.make(
                Movie,
                orj_title=f"{i}",
            )
            cls.movies.append(movie)

    def setUp(self):
        self.client = Client()
        self.url = reverse("film:movies_list")

    def test_movies_pagination(self):
        response = self.client.get(f"{self.url}?page=3&page_size=10")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 5)

    def test_movies_pagination_by_default_paginate(self):
        response = self.client.get(f"{self.url}?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 21)

        response = self.client.get(f"{self.url}?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 4)

    def test_movies_pagination_by_custom_paginate(self):
        response = self.client.get(f"{self.url}?page=1&page_size=10")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 10)

    def test_movies_pagination_by_out_of_range_paginate(self):
        response = self.client.get(f"{self.url}?page=1&page_size=5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 7)

        response = self.client.get(f"{self.url}?page=1&page_size=30")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 21)

    def test_movies_pagination_by_invalid_paginate(self):
        response = self.client.get(f"{self.url}?page=1&page_size=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 21)

    def test_movies_pagination_with_negetive_paginate(self):
        response = self.client.get(f"{self.url}?page=1&page_size=-1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 7)

    def test_movies_pagination_with_float_paginate(self):
        response = self.client.get(f"{self.url}?page=1&page_size=10.5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 21)

    def test_movies_pagination_with_out_of_range_page(self):
        response = self.client.get(f"{self.url}?page=7")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 4)

    def test_movies_pagination_with_zero_page(self):
        response = self.client.get(f"{self.url}?page=0")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 4)

    def test_movies_pagination_with_negetive_page(self):
        response = self.client.get(f"{self.url}?page=-1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 4)

    def test_movies_pagination_with_invalid_page(self):
        response = self.client.get(f"{self.url}?page=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 21)

    def test_movies_pagination_next_page(self):
        response = self.client.get(f"{self.url}?page=1")
        self.assertEqual(response.status_code, 200)

        page = response.context["page_obj"]

        self.assertEqual(page.has_next(), True)
        self.assertEqual(page.next_page_number(), 2)
        self.assertEqual(page.has_previous(), False)

    def test_movies_pagination_pre_page(self):
        response = self.client.get(f"{self.url}?page=2")
        self.assertEqual(response.status_code, 200)

        page = response.context["page_obj"]

        self.assertEqual(page.has_next(), False)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.previous_page_number(), 1)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class MoviesListViewAjaxTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movies = []
        for i in range(1, 11):
            movie = baker.make(
                Movie,
                orj_title=f"{i}",
                rate=5.0,
            )
            cls.movies.append(movie)

        baker.make(
            Movie,
            orj_title=f"{11}",
            adult=True,
            rate=6.0
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("film:movies_list")

    def test_movies_ajax_response_is_jsonresponse(self):
        response = self.client.get(
            self.url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_movies_ajax_context(self):
        response = self.client.get(
            f"{self.url}?page_size=7",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertIn("html", data)
        self.assertIn("has_next", data)
        self.assertIn("next_page", data)
        self.assertIsInstance(data["html"], str)
        self.assertIsInstance(data["has_next"], bool)
        self.assertIsInstance(data["next_page"], int)

        self.assertEqual(data["has_next"], True)
        self.assertEqual(data["next_page"], 2)

        response = self.client.get(
            f"{self.url}?page_size=7&page={data['next_page']}",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertEqual(data["has_next"], False)
        self.assertEqual(data["next_page"], None)

    @patch("film.views.render_to_string")
    def test_ajax_renders_movie_cards_template(self, mock_render_to_string):
        mock_render_to_string.return_value = "<div>movies html</div>"

        response = self.client.get(
            self.url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

        mock_render_to_string.assert_called_once()

        template_name = mock_render_to_string.call_args.args[0]
        self.assertEqual(template_name, "ajax/movie_cards.html")

    @patch("film.views.render_to_string")
    def test_movies_ajax_with_filters(self, mock_render_to_string):
        mock_render_to_string.return_value = "<div>fake html</div>"

        response = self.client.get(
            f"{self.url}?adult=true",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        mock_render_to_string.assert_called_once()
        context = mock_render_to_string.call_args.args[1]
        movies = context["movies"]
        self.assertEqual(movies[0].orj_title, "11")

    @patch("film.views.render_to_string")
    def test_movies_ajax_with_ordering(self, mock_render_to_string):
        mock_render_to_string.return_value = "<div>fake html</div>"

        response = self.client.get(
            f"{self.url}?ordering=-rate",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        mock_render_to_string.assert_called_once()
        context = mock_render_to_string.call_args.args[1]
        movies = context["movies"]
        self.assertEqual(movies[0].orj_title, "11")


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class MoviesListViewCacheTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre1 = baker.make(Genre, id=1, en_name="1")
        cls.genre2 = baker.make(Genre, id=2, en_name="2")
        cls.movie1 = baker.make(Movie, orj_title="1", genres=[cls.genre1], release_date=date(2020, 3, 3))
        cls.movie2 = baker.make(Movie, orj_title="2", genres=[cls.genre1], release_date=date(2020, 3, 3))
        cls.movie3 = baker.make(Movie, orj_title="3", adult=True, genres=[cls.genre1], release_date=date(2020, 3, 3))
        cls.movie4 = baker.make(Movie, orj_title="4", adult=True, genres=[cls.genre2], release_date=date(2021, 3, 3))
        cls.movie5 = baker.make(Movie, orj_title="5", adult=True, genres=[cls.genre2], release_date=date(2021, 3, 3))

    def setUp(self):
        self.client = Client()
        self.url = reverse("film:movies_list")

    def test_movies_cache_key_for_url(self):
        cache.clear()

        query_params = [
            ("adult", "true"),
            ("genre_id", "1"),
            ("ordering", "-rate"),
            ("release_date", "2020"),
        ]

        response = self.client.get(
            self.url,
            data=query_params,
        )

        self.assertEqual(response.status_code, 200)

        movies = list(response.context["movies"])

        expected_params = sorted(query_params)
        expected_hash = hashlib.sha256(
            str(expected_params).encode("utf-8")
        ).hexdigest()

        cache_key = f"movies_list_{expected_hash}"
        cached_movies = list(cache.get(cache_key))

        self.assertIsNotNone(cached_movies)
        self.assertEqual(movies, cached_movies)

    def test_movies_cache_key_same_query_different_order(self):
        cache.clear()

        request_1 = self.client.get(
            self.url,
            data=[
                ("ordering", "-rate"),
                ("release_date", "2020"),
                ("adult", "true"),
                ("genre_id", "1"),
            ],
        ).wsgi_request

        request_2 = self.client.get(
            self.url,
            data=[
                ("adult", "true"),
                ("genre_id", "1"),
                ("ordering", "-rate"),
                ("release_date", "2020"),
            ],
        ).wsgi_request

        view = MoviesList()

        cache_key_1 = view.get_cache_key(request_1)
        cache_key_2 = view.get_cache_key(request_2)

        self.assertEqual(cache_key_1, cache_key_2)

    def test_movies_cache_key_different_query(self):
        cache.clear()

        request_1 = self.client.get(
            self.url,
            data=[
                ("adult", "true"),
                ("genre_id", "1"),
                ("ordering", "-rate"),
                ("release_date", "2020"),
            ],
        ).wsgi_request

        request_2 = self.client.get(
            self.url,
            data=[
                ("adult", "true"),
                ("genre_id", "2"),
                ("ordering", "-rate"),
                ("release_date", "2020"),
            ],
        ).wsgi_request

        view = MoviesList()

        cache_key_1 = view.get_cache_key(request_1)
        cache_key_2 = view.get_cache_key(request_2)

        self.assertNotEqual(cache_key_1, cache_key_2)

    def test_movies_set_cache(self):
        cache.clear()
        data = [
            ("genre_id", "1"),
            ("release_date", "2020"),
        ]

        expected_params = sorted(data)
        expected_hash = hashlib.sha256(
            str(expected_params).encode("utf-8")
        ).hexdigest()

        cache_key = f"movies_list_{expected_hash}"
        cached_movies = cache.get(cache_key)

        self.assertEqual(cached_movies, None)

        response = self.client.get(self.url, data=data)
        movies = list(response.context["movies"])
        cached_movies = list(cache.get(cache_key))

        self.assertEqual(movies, cached_movies)

    def test_movies_geres_cache(self):
        cache.clear()

        cached_genres = cache.get("genres")
        self.assertEqual(cached_genres, None)

        response = self.client.get(self.url)

        genres = list(response.context["genres"])
        cached_genres = list(cache.get("genres"))
        self.assertEqual(cached_genres, genres)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class MoviesListViewContextTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre1 = baker.make(Genre, id=1, en_name="1", fa_name="یک")
        cls.genre2 = baker.make(Genre, id=2, en_name="2", fa_name="دو")
        cls.movie1 = baker.make(Movie, orj_title="1", adult=False, genres=[cls.genre1], release_date=date(2020, 3, 3))
        cls.movie2 = baker.make(Movie, orj_title="2", adult=False, genres=[cls.genre2], release_date=date(2020, 3, 3))
        cls.movie3 = baker.make(Movie, orj_title="3", adult=True, genres=[cls.genre1], release_date=date(2021, 3, 3))
        cls.movie4 = baker.make(Movie, orj_title="4", adult=True, genres=[cls.genre2], release_date=date(2021, 3, 3))
        cls.movie5 = baker.make(Movie, orj_title="5", adult=False, genres=[cls.genre1], release_date=date(2021, 3, 3))

    def setUp(self):
        self.client = Client()
        self.url = reverse("film:movies_list")
        self.data = [
            ("genre_id", "1"),
            ("release_date", "2020"),
            ("adult", "false"),
            ("ordering", "-rate"),
            ("page", "1"),
            ("page_size", "7"),
        ]

    def get_context(self):
        cache.clear()

        response = self.client.get(self.url, data=self.data)
        return response.context

    def test_movies_context_contain_values(self):
        context = self.get_context()
        keys = [
            "selected_genre",
            "selected_adult",
            "selected_release_date",
            "selected_ordering",
            "genre_label",
            "adult_label",
            "release_date_label",
            "ordering_label",
            "genres",
            "years",
            "page_size_param",
            "movies",
            "page_obj",
            "paginator",
            "page_size",
        ]
        for i in keys:
            self.assertIn(i, context)

    def test_movies_context_selected_filters_orders(self):
        context = self.get_context()

        self.assertEqual(context.get("selected_genre"), "1")
        self.assertEqual(context.get("selected_adult"), "false")
        self.assertEqual(context.get("selected_release_date"), "2020")
        self.assertEqual(context.get("selected_ordering"), "-rate")

    def test_movies_context_labels(self):
        context = self.get_context()

        self.assertEqual(context.get("genre_label"), "یک")
        self.assertEqual(context.get("adult_label"), "کودک و نوجوان")
        self.assertEqual(context.get("release_date_label"), "2020")
        self.assertEqual(context.get("ordering_label"), 'بیشترین امتیاز')

    def test_movies_context_lists(self):
        context = self.get_context()

        movies = Movie.objects.all()
        years = [
            date_obj.year
            for date_obj in movies.filter(release_date__isnull=False).dates('release_date', 'year')
        ]
        genres = list(Genre.objects.all())
        movies = Movie.objects.filter(
            genres__id=1,
            release_date=date(2020, 3, 3),
            adult=False,
        ).order_by("-rate")
        movies = list(movies)

        self.assertEqual(movies, list(context["movies"]))
        self.assertEqual(years, list(context["years"]))
        self.assertEqual(genres, list(context["genres"]))

    def test_movies_context_page_objs(self):
        context = self.get_context()

        self.assertIsInstance(context.get("page_obj"), Page)
        self.assertIsInstance(context.get("paginator"), Paginator)
        self.assertEqual(context.get("page_size"), 7)
        self.assertEqual(context.get("page_size_param"), "7")
