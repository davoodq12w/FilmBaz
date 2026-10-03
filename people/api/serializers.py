from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from people.models import CrewMember, Cast, MovieCrew


class CrewMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for crew members.
    """
    image = serializers.ImageField(allow_null=True, use_url=True, required=False)

    class Meta:
        model = CrewMember
        fields = ["id", "en_name", "fa_name", "slug", "image"]


class CastSerializer(serializers.ModelSerializer):
    """
    Serializer for casts.
    """
    image = serializers.ImageField(allow_null=True, use_url=True, required=False)

    class Meta:
        model = Cast
        fields = ["id", "en_name", "fa_name", "slug", "image"]


class MovieCrewSerializer(serializers.ModelSerializer):
    """
    Serializer for movie crews.
    """
    crew = serializers.SerializerMethodField()

    class Meta:
        model = MovieCrew
        fields = ["role", 'crew']

    @extend_schema_field(CrewMemberSerializer)
    def get_crew(self, obj: MovieCrew):
        """
        method used for getting crew members data.
        """
        crew = obj.crew
        if crew:
            return CrewMemberSerializer(crew).data
        else:
            return None
