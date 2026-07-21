from django.db import models
from django_resized import ResizedImageField
from account.models import FilmBazUser
from people.models import MovieCrew


class Genre(models.Model):
    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ['en_name']

    def __str__(self):
        return f"{self.en_name}/{self.fa_name}"

    def top_3_movies(self):
        return self.movies.all().order_by("-rate")[:3]


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
    users_liked = models.ManyToManyField(FilmBazUser, related_name="likes", blank=True)
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
        movie_crew = self.movie_crews.filter(
            role=MovieCrew.CrewRole.DIRECTOR
        ).first()

        return movie_crew.crew if movie_crew else None

    @property
    def get_producer(self):
        movie_crew = self.movie_crews.filter(
            role=MovieCrew.CrewRole.PRODUCER
        ).first()

        return movie_crew.crew if movie_crew else None

    @property
    def get_writer(self):
        movie_crew = self.movie_crews.filter(
            role=MovieCrew.CrewRole.WRITER
        ).first()

        return movie_crew.crew if movie_crew else None


class MovieFile(models.Model):
    episode = models.PositiveSmallIntegerField(default=1)
    season = models.PositiveSmallIntegerField(default=1)
    seen_by = models.ManyToManyField(FilmBazUser, related_name="seened_movies", blank=True)
    file = models.FileField(upload_to=f"movies/movies/", )
    movie = models.ForeignKey(Movie, related_name="files", on_delete=models.CASCADE)
    hour = models.PositiveSmallIntegerField(default=0)
    minute = models.PositiveSmallIntegerField(default=0)
    second = models.PositiveSmallIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.movie.orj_title}:S{self.season}:E{self.episode}"


class MovieTrailer(models.Model):
    seen_by = models.ManyToManyField(FilmBazUser, related_name="seened_trailers", blank=True)
    file = models.FileField(upload_to=f"movies/trailers/", )
    movie = models.ForeignKey(Movie, related_name="trailer", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class WatchTime(models.Model):
    user = models.ForeignKey(FilmBazUser, related_name="watch_times", on_delete=models.CASCADE)
    movie = models.ForeignKey(MovieFile, related_name="watch_times", on_delete=models.CASCADE)
    hour = models.PositiveSmallIntegerField(default=0)
    minute = models.PositiveSmallIntegerField(default=0)
    second = models.PositiveSmallIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}-{str(self.movie)}/{self.hour}:{self.minute}:{self.second}"


class Comment(models.Model):
    text = models.TextField(max_length=300)
    movie = models.ForeignKey(Movie, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(FilmBazUser, related_name="comments", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
