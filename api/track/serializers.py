from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from api.track.models import Track, Venue


class VenueSerializer(ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'
        extra_kwargs = {
            'is_available': {'required': False},
            'description': {'required': False},
        }

class TrackSerializer(ModelSerializer):
    venue = PrimaryKeyRelatedField(queryset=Venue.objects.all(), many=False)
    class Meta:
        model = Track
        fields = '__all__'
        extra_kwargs = {
            'description': {'required': False},
            'is_available': {'required': False},
        }