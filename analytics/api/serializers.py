from rest_framework import serializers


class ShareIntractionSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField(read_only=True)
    movie_slug = serializers.SlugField(required=True)
