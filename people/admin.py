from django.contrib import admin
from .models import Cast, CrewMember


@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'slug']
    search_fields = ["fa_name", "en_name", "slug"]
    raw_id_fields = ['movies']


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = (
        "en_name",
        "fa_name",
        "role",
        "movies_count",
    )

    list_filter = ("role",)

    search_fields = (
        "en_name",
        "fa_name",
    )

    prepopulated_fields = {
        "slug": ("en_name",)
    }

    filter_horizontal = ("movies",)

    def movies_count(self, obj):
        return obj.movies.count()

    movies_count.short_description = "Movies"
