from django.contrib import admin
from .models import *


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'tmdb_rate', 'release_date', ]
    ordering = ['-release_date', 'title']
    list_filter = ['release_date', 'country', 'tmdb_rate']
    search_fields = ['release_date', 'description', 'title', 'country']
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
