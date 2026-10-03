from django.contrib import admin
from .models import Cast, CrewMember, MovieCrew


@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    """
    Admin panel for Cast model.
    """
    list_display = ['fa_name', 'slug']
    search_fields = ["fa_name", "en_name", "slug"]
    raw_id_fields = ['movies']


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    """
    Admin panel for CrewMember model.
    """
    list_display = ["fa_name", "slug"]
    search_fields = ["fa_name", "en_name", "slug"]


@admin.register(MovieCrew)
class MovieCrewAdmin(admin.ModelAdmin):
    """
    Admin panel for MovieCrew model.
    """
    list_display = ["crew__fa_name", "movie__fa_title", "role"]
