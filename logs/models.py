from django.db import models
from django.contrib.contenttypes.models import ContentType
from account.models import FilmBazUser


class Log(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(FilmBazUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # Order logs by timestamp in descending order

    def __str__(self):
        return f"{self.get_action_display()} on {self.content_type.model} ({self.object_id}) by {self.user}"
