from rest_framework import serializers
from film.models import Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "en_name", "fa_name", "slug"]
        read_only_fields = ["id", "en_name", "fa_name", "slug"]
