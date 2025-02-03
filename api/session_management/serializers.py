from django.apps import apps
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
                raise serializers.ValidationError("Capacity is greater than track capacity.")
        else:
            raise serializers.ValidationError("This field is required.")
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
                                              "please choose different track or time.")
        return attrs


class SessionSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True)
    speakers = serializers.SerializerMethodField()
    capacity = serializers.SerializerMethodField()

    def get_speakers(self, obj):
        speakers = obj.speakers.prefetch_related('profile').all()
        return [{
            'name': speaker.profile.get_full_name(),
            'role': speaker.role,
            'occupation': speaker.profile.occupation
        } for speaker in speakers]

    def get_capacity(self, obj):
        return obj.get_capacity()

    class Meta:
        model = Session
        fields = '__all__'


class CreateAndUpdateSessionSerializer(serializers.ModelSerializer):
    events = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        many=True
    )
    speakers = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('users', 'speaker').objects.all(),
        many=True
    )

    class Meta:
        model = Session
        fields = '__all__'

    def validate_events(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def validate_speakers(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value


