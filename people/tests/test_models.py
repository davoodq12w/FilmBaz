from django.test import TestCase
from people.models import Cast, CrewMember, MovieCrew
from model_bakery import baker
from film.models import Movie


class CastModelTest(TestCase):

    def test_srt_method(self):
        cast = Cast.objects.create(
            fa_name="بازیگر",
            en_name="actor",
            slug="actor",
        )
        self.assertEqual(str(cast), "actor")


class CrewMemberModelTest(TestCase):

    def test_srt_method(self):
        crew = CrewMember.objects.create(
            fa_name="عامل",
            en_name="crew",
            slug="crew",
        )
        self.assertEqual(str(crew), "crew")


class MovieCrewModelTest(TestCase):

    def test_srt_method(self):
        crew = CrewMember.objects.create(
            fa_name="عامل",
            en_name="crew",
            slug="crew",
        )
        movie = baker.make(Movie, orj_title="batman")

        obj = MovieCrew.objects.create(
            movie=movie,
            crew=crew,
            role=MovieCrew.CrewRole.DIRECTOR
        )
        self.assertEqual(
            str(obj),
            "batman - crew (director)"
        )
