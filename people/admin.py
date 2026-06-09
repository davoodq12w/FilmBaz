from django.contrib import admin
from .models import Cast, CrewMember, MovieCrew


@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'slug']
    search_fields = ["fa_name", "en_name", "slug"]
    raw_id_fields = ['movies']


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ["fa_name", "slug"]
    search_fields = ["fa_name", "en_name", "slug"]


@admin.register(MovieCrew)
class MovieCrewAdmin(admin.ModelAdmin):
    list_display = ["crew__fa_name", "movie__fa_title", "role"]
