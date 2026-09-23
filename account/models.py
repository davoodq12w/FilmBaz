from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django_resized import ResizedImageField


# Create your models here.

class FilmBazUserManager(BaseUserManager):
    """
    Base Manager used for Custom type of User
    """

    def create_user(self, username, password=None, **extra_fields):
        """
        creating new user with extra fields
        """
        if not username:
            raise ValueError("username must be exists")
        user = self.model(username=username, **extra_fields)  # create user obj with extra fields
        user.set_password(password)  # set the hashed password for user obj
        user.save(using=self._db)  # writing user object in to the DataBase
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        creating superuser with extra fields
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # make sure to user is being superuser.
        if not extra_fields.get("is_staff"):
            raise ValueError("is_staff must be True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("is_superuser must be True")

        # creating user by useing create_user method and sending the new extra fields for that.
        return self.create_user(username, password, **extra_fields)


class FilmBazUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom UserModel with extra fields
    """
    username = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=11, unique=True)
    email = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    image = ResizedImageField(upload_to="profile_images/%Y/%m/%d", quality=100, crop=["middle", "center"],
                              size=[500, 500], null=True)
    favorite_genres = models.ManyToManyField(
        "film.Genre",
        related_name='fans',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"

    # required fields being required even in management commands.
    # set required fields for creation of user and superuser.
    REQUIRED_FIELDS = ['phone']

    objects = FilmBazUserManager()  # set custom Manager

    class Meta:
        ordering = ['username', '-created']
        indexes = [
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.username


class UserRecommendation(models.Model):
    """
    Model saves user recommendations.
    recommendations come from ml_service and filled with celery beat task.
    """
    user = models.OneToOneField(
        FilmBazUser,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )
    # the movies are to meny and JsonField is better than ForeignKeyFields
    recommendations = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)


class Ticket(models.Model):
    """
    Model for Ticker of users
    """

    class Subject(models.TextChoices):
        """
        enumirate of ticket subject.
        """
        CRITICISM = 'Criticism', 'انتقاد'
        PROPOSAL = 'Proposal', 'پیشنهاد'
        REPORT = 'Report', ' گزارش'

    subject = models.CharField(choices=Subject.choices, max_length=9)
    text = models.TextField(max_length=2000)
    phone = models.CharField(max_length=11)
    email = models.EmailField(max_length=50)
