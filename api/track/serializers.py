from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer

from api.track.models import Track, Venue
from api.utils.helpers import get_entity_href_serializer, get_entity


class VenueSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Venue
        fields = (
            'name',
            'location',
            'description',
            'is_available',
            'href',
        )
        extra_kwargs = {
            'is_available': {'required': False},
            'description': {'required': False},
            'href': {'lookup_field': 'id'},
        }

class TrackSerializer(HyperlinkedModelSerializer):
    venue = get_entity_href_serializer(model_class=Venue)
    class Meta:
        model = Track
        fields = (
            'venue',
            'href',
            'name',
            'description',
            'is_available',
            'capacity'
        )
        extra_kwargs = {
            'description': {'required': False},
            'is_available': {'required': False},
            'href': {'lookup_field': 'id'},
        }

    def create(self, validated_data):
        validated_data['venue'] = get_entity(Venue, self.initial_data.get('venue', {}).get('href'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['venue'] = get_entity(Venue, self.initial_data.get('venue', {}).get('href'))
        instance = super().update(instance, validated_data)
        return instance