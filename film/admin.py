from django.contrib import admin
from .models import *


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['fa_title', 'rate', 'release_date']
    ordering = ['-release_date', 'fa_title']
    list_filter = ['release_date', 'country', 'rate']
    search_fields = ['release_date', 'description', 'fa_title', 'orj_title', 'country']
    raw_id_fields = ['genres']
    date_hierarchy = 'release_date'
    inlines = [CommentInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'slug']
    ordering = ['en_name']
    search_fields = ['fa_name', 'en_name', 'slug']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'created', 'text']
    search_fields = ["text"]
    raw_id_fields = ['user', 'movie']


@admin.register(MovieTrailer)
class MovieTrailerAdmin(admin.ModelAdmin):
    list_display = ["movie__orj_title", "timestamp"]
    search_fields = ["movie__orj_title", "movie__fa_title", "movie__slug"]
    list_filter = ["movie__orj_title"]


@admin.register(MovieFile)
class MovieFileAdmin(admin.ModelAdmin):
    list_display = ["movie__orj_title", "season", "episode", "timestamp"]
    search_fields = ["movie__orj_title", "movie__fa_title", "movie__slug"]


@admin.register(WatchTime)
class WatchTimeAdmin(admin.ModelAdmin):
    list_display = ["movie__orj_title", "user__username", "timestamp"]
    search_fields = ["movie__orj_title", "movie__fa_title", "movie__slug", "user__username", "user__email",
                     "user__phone"]
    list_filter = ["movie__orj_title", "user__username"]
