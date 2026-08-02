from django.contrib import admin
from .models import *


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ["user__username", "movie__slug", "interaction_type", "timestamp"]
    search_fields = ["user__username", "user__phone", "user__email", "movie__slug", "movie__description",
                     "movie__fa_title", "movie__orj_title", "interaction_type"]
    date_hierarchy = "timestamp"
    list_filter = ["user__username", "movie__slug", "interaction_type"]


@admin.register(WatchInteraction)
class WatchInteractionAdmin(admin.ModelAdmin):
    list_display = ["user__username", "episode__movie__orj_title", "interaction_type", "timestamp"]
    search_fields = ["user__username", "user__phone", "user__email", "episode__movie__slug",
                     "episode__movie__fa_title", "episode__movie__orj_title", "interaction_type"]
    date_hierarchy = "timestamp"
    list_filter = ["user__username", "episode__movie__slug", "interaction_type"]
