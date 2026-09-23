from rest_framework import serializers
from analytics.models import Interaction


class InteractionSerializer(serializers.Serializer):
    """
    Seriailzer for create Interaction object
    """
    movie_id = serializers.IntegerField(read_only=True)
    movie_slug = serializers.SlugField(required=True)
    interaction_type = serializers.ChoiceField(
        choices=Interaction.Type.choices,
        required=True
    )
