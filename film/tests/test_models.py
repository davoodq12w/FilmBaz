from datetime import date
from django.test import TestCase
from film.models import Genre, Movie
from people.models import CrewMember, MovieCrew



class GenreModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.genre = Genre.objects.create(
            fa_name='اکشن',
            en_name='Action',
            slug='action'
        )

    def test_genre_str_method(self):
        self.assertEqual(
            str(self.genre),
            'Action/اکشن'
        )


class MovieModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie = Movie.objects.create(
            fa_title="بتمن",
            orj_title="Batman",
            slug="batman",
            release_date=date(2022, 1, 1)
        )

    def test_str_method(self):
        self.assertEqual(
            str(self.movie),
            f"بتمن - {self.movie.release_date}"
        )

    def test_poster_url_method(self):
        movie = self.movie
        self.assertEqual(
            movie.poster_url,
            None
        )
        test_url = "test/test.png"
        movie.poster = test_url
        movie.save()
        movie.refresh_from_db()
        self.assertIn(
            test_url,
            movie.poster_url
        )

    def test_backdrop_url_method(self):
        movie = self.movie
        self.assertEqual(
            movie.backdrop_url,
            None
        )
        test_url = "test/test.png"
        movie.backdrop = test_url
        movie.save()
        movie.refresh_from_db()
        self.assertIn(
            test_url,
            movie.backdrop_url
        )

    def test_get_director_method(self):
        movie = self.movie
        self.assertEqual(
            movie.get_director,
            None
        )
        director = CrewMember.objects.create(
            fa_name="کارگردان",
            en_name="Director",
            slug="director"
        )
        MovieCrew.objects.create(
            movie=movie,
            crew=director,
            role=MovieCrew.CrewRole.DIRECTOR
        )
        self.assertEqual(
            movie.get_director,
            director
        )

    def test_get_producer_method(self):
        movie = self.movie
        self.assertEqual(
            movie.get_producer,
            None
        )
        producer = CrewMember.objects.create(
            fa_name="تهیه کننده",
            en_name="Producer",
            slug="producer"
        )
        MovieCrew.objects.create(
            movie=movie,
            crew=producer,
            role=MovieCrew.CrewRole.PRODUCER
        )
        self.assertEqual(
            movie.get_producer,
            producer
        )

    def test_get_writer_method(self):
        movie = self.movie
        self.assertEqual(
            movie.get_writer,
            None
        )
        writer = CrewMember.objects.create(
            fa_name="نویسنده",
            en_name="Writer",
            slug="writer"
        )
        MovieCrew.objects.create(
            movie=movie,
            crew=writer,
            role=MovieCrew.CrewRole.WRITER
        )
        self.assertEqual(
            movie.get_writer,
            writer
        )
