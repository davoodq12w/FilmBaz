from django.test import TestCase, Client, override_settings
from model_bakery import baker
from film.models import Movie, Genre
from datetime import timedelta, date
from django.utils import timezone
from django.shortcuts import reverse


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
    ...