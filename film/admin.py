from django.contrib import admin
from .models import *


# Register your models here.


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'rate', 'year', 'director']
    ordering = ['-year', 'title']
    list_filter = ['year', 'director', 'country', 'rate']
    search_fields = ['director', 'producer', 'year', 'composer', 'editor', 'description', 'title', 'country']
    raw_id_fields = ['genre']
    date_hierarchy = 'year'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    ordering = ['name']
