from django.db.models import Q
from rest_framework import serializers

from api.session_management.models import Event, Session
from api.track.models import Track


class EventSerializer(serializers.ModelSerializer):
    track = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all())

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'description': {'required': False},
        }

    def validate_capacity(self, value):
        track_id = self.initial_data.get('track')
        if track_id:
            track = Track.objects.get(id=track_id)
            if value > track.capacity:
                raise serializers.ValidationError("Capacity is greater than track capacity")
        else:
            raise serializers.ValidationError("This field is required")
        return value

    def validate(self, attrs):
        date = attrs.get('date')
        track_id = attrs.get('track')
        existing_events_in_time_occurrence = Event.objects.filter(
            Q(track_id=track_id, date=date),
            Q(
                Q(start_time__gte=attrs.get('end_time')) |
                Q(end_time__gte=attrs.get('start_time'))
            )
        ).exists()
        if existing_events_in_time_occurrence:
            raise serializers.ValidationError("Track already has event at this time, "
                                              "please choose different track or time")
        return attrs


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
