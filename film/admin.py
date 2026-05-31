from django.contrib import admin
from .models import *


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'tmdb_rate', 'year', ]
    ordering = ['-year', 'title']
    list_filter = ['year', 'country', 'tmdb_rate']
    search_fields = ['year', 'description', 'title', 'country']
    raw_id_fields = ['genres']
    date_hierarchy = 'year'
    inlines = [CommentInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'slug']
    ordering = ['en_name']
    search_fields = ['fa_name', 'en_name', 'slug']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'slug']
    ordering = ['en_name']
    search_fields = ['fa_name', 'en_name', 'slug']



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'created', 'text']
    search_fields = ["text"]
    raw_id_fields = ['user', 'movie']
