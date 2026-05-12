from django.db import models
from account.models import FilmBazUser


# Create your models here.

class SupportSession(models.Model):
    user = models.ForeignKey(
        FilmBazUser,
        on_delete=models.SET_NULL,
        related_name='user_support_sessions',
        null=True,
        blank=True,
    )
    supporter = models.ForeignKey(
        FilmBazUser,
        on_delete=models.SET_NULL,
        related_name='support_sessions',
        null=True,
        blank=True,
    )
    session_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Status(models.TextChoices):
        CLOSED = "closed", "Closed"
        OPEN = "open", "Open"
        PENDING = "pending", "Pending"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    def __str__(self):
        return f"SupportSession:{self.user.username if self.user else 'NoUser'}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'session_date'],
                name='unique_user_session_per_day'
            )
        ]
        ordering = ['-created_at']


class SupportMessage(models.Model):
    sender = models.ForeignKey(
        FilmBazUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='support_messages',
    )
    session = models.ForeignKey(SupportSession, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(max_length=1000)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
