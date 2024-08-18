from django.contrib import admin
from .models import *


# Register your models here.

class FileInline(admin.TabularInline):
    model = File
    extra = 0


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'rate', 'year', 'director']
    ordering = ['-year', 'title']
    list_filter = ['year', 'director', 'country', 'rate']
    search_fields = ['director', 'producer', 'year', 'composer', 'editor', 'description', 'title', 'country']
    raw_id_fields = ['genres']
    date_hierarchy = 'created'
    inlines = [FileInline, CommentInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    ordering = ['name']


@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ["name"]
    raw_id_fields = ['movies']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'created', 'text']
    search_fields = ["text"]
    raw_id_fields = ['user', 'movie']
