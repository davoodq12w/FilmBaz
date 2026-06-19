from django.test import TestCase, Client, override_settings
from model_bakery import baker
from film.models import Movie, Genre
from datetime import timedelta, date
from django.utils import timezone
from django.shortcuts import reverse
from django.http import JsonResponse
from unittest.mock import patch


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


