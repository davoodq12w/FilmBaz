from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django_resized import ResizedImageField


# Create your models here.

class FilmBazUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("username must be exists")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("is_staff must be True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("is_superuser must be True")
        return self.create_user(username, password, **extra_fields)


class FilmBazUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=11)
    email = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    image = ResizedImageField(upload_to="profile_images/", quality=100, crop=["middle", "center"], size=[500, 500])

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['phone']

    objects = FilmBazUserManager()

    class Meta:
        ordering = ['username', '-created']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.username


class Ticket(models.Model):

    class Subject(models.TextChoices):
        CRITICISM = 'Criticism', 'انتقاد'
        PROPOSAL = 'Proposal', 'پیشنهاد'
        REPORT = 'Report', ' گزارش'

    subject = models.CharField(choices=Subject.choices)
    text = models.TextField(max_length=2000)
    phone = models.CharField(max_length=11)
    email = models.EmailField(max_length=50)

