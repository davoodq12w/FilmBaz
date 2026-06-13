from django.db import models
from django_resized import ResizedImageField
from account.models import FilmBazUser


class Genre(models.Model):
    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )

    class Meta:
        ordering = ['en_name']
        indexes = [
            models.Index(fields=['en_name']),
        ]

    def __str__(self):
        return f"{self.en_name}/{self.fa_name}"


class Movie(models.Model):
    # ----------------------------------------------------------------
    poster = ResizedImageField(upload_to="movies/posters/", size=[300, 400], crop=["middle", "center"], quality=100,
                               null=True, blank=True)
    backdrop = ResizedImageField(upload_to="movies/backdrop/", size=[1600, 900], crop=["middle", "center"], quality=100,
                                 null=True, blank=True)
    # ----------------------------------------------------------------
    fa_title = models.CharField(max_length=200)
    orj_title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )
    description = models.TextField(max_length=2000, null=True, blank=True)
    rate = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    release_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    runtime = models.PositiveSmallIntegerField(null=True, blank=True)
    # ----------------------------------------------------------------
    users_saved = models.ManyToManyField(FilmBazUser, related_name="saves", blank=True)
    # ----------------------------------------------------------------
    is_serie = models.BooleanField(default=False)
    adult = models.BooleanField(default=False)
    # ----------------------------------------------------------------
    genres = models.ManyToManyField(Genre, related_name="movies")
    # ----------------------------------------------------------------
    created = models.DateField(auto_now_add=True)
    crew_members = models.ManyToManyField(
        'people.CrewMember',
        through="people.MovieCrew",
        related_name="movies",
        blank=True
    )

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.fa_title} - {self.release_date}"

    @property
    def poster_url(self):
        if self.poster:
            return self.poster.url

        return None

    @property
    def backdrop_url(self):
        if self.backdrop:
            return self.backdrop.url

        return None

    @property
    def get_director(self):
        try:
            return self.movie_crews.filter(role="director").first().crew
        except:
            return None

    @property
    def get_producer(self):
        try:
            return self.movie_crews.filter(role="producer").first().crew
        except:
            return None

    @property
    def get_writer(self):
        try:
            return self.movie_crews.filter(role="writer").first().crew
        except:
            return None


class Comment(models.Model):
    text = models.TextField(max_length=300)
    movie = models.ForeignKey(Movie, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(FilmBazUser, related_name="comments", on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
