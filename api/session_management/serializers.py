from django.db.models import Q
from django.urls import reverse
from rest_framework import serializers

from api.session_management.models import Event, Session, Speaker
from api.track.models import Track
from api.track.serializers import TrackSerializer
from api.utils.choices import Gender, MaritalStatus, Responsibility
from api.utils.helpers import get_entity_href_serializer, get_entity_id, get_entity
from api.utils.validators import PhoneNumberValidator


class EventSerializer(serializers.HyperlinkedModelSerializer):
    track = get_entity_href_serializer(Track)
    speakers = serializers.SerializerMethodField()

    def get_speakers(self, obj: Event):
        '''
        :param obj: event object
        :return: short information regarding the speakers
        '''
        speakers = obj.speakers.select_related('profile')
        return [{
            'name': speaker.profile.get_full_name(),
            'role': speaker.role,
            'occupation': speaker.profile.occupation
        } for speaker in speakers]

    class Meta:
        model = Event
        fields = (
            'href',
            'name',
            'description',
            'track',
            'speakers',
            'date',
            'start_time',
            'end_time',
            'capacity',
        )
        extra_kwargs = {
            'href': {'lookup_field': 'id'},
        }


class CreateAndUpdateEventSerializer(serializers.HyperlinkedModelSerializer):
    track = get_entity_href_serializer(Track, many=False)
    speakers = get_entity_href_serializer(Speaker, many=True)
    href = serializers.SerializerMethodField()

    def get_href(self, obj: Event):
        return reverse('event-detail', kwargs={'id': obj.id})

    class Meta:
        model = Event
        fields = (
            'href',
            'name',
            'description',
            'track',
            'speakers',
            'date',
            'start_time',
            'end_time',
            'capacity'
        )
        extra_kwargs = {
            'description': {'required': False},

        }

    def validate_capacity(self, value):
        if isinstance(self.initial_data.get('track'), dict):
            track_id = get_entity_id(self.initial_data.get('track', {}).get('href'))
            if track_id:
                track = Track.objects.get(id=track_id)
                if value > track.capacity:
                    raise serializers.ValidationError("Capacity is greater than track capacity.")
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def validate_track(self, value):
        date = self.initial_data.get('date')
        if not value:
            raise serializers.ValidationError("This field is required.")
        if not isinstance(self.initial_data.get('track'), dict):
            raise serializers.ValidationError("Incorrect format.")

        track_id = get_entity_id(self.initial_data.get('track', {}).get('href'))
        existing_events_in_time_occurrence = Event.objects.filter(
            Q(track_id=track_id, date=date),
            Q(
                Q(start_time__gte=self.initial_data.get('end_time')) |
                Q(end_time__gte=self.initial_data.get('start_time'))
            )
        )
        if self.instance:
            existing_events_in_time_occurrence = existing_events_in_time_occurrence.exclude(id=self.instance.id)
        if existing_events_in_time_occurrence.exists():
            raise serializers.ValidationError("Track already has event at this time, "
                                              "please choose different track or time.")
        return value

    def validate_speakers(self, values):
        if not values or not isinstance(values, list):
            raise serializers.ValidationError("This field is required.")
        else:
            date = self.initial_data.get('date')
            speaker_ids = [get_entity_id(value.get('href')) for value in self.initial_data.get('speakers', [])]
            query = Event.objects.filter(
                Q(date=date),
                Q(
                    Q(start_time__gte=self.initial_data.get('end_time')) |
                    Q(end_time__gte=self.initial_data.get('start_time'))
                ),
                Q(speakers__in=speaker_ids)
            ).distinct()
            if self.instance:
                query = query.exclude(id=self.instance.id)
            existing_events_in_time_occurrence = query.exists()
            if existing_events_in_time_occurrence:
                raise serializers.ValidationError("Some of the speaker(s) already has event at this time, "
                                                  "please choose different speaker(s) or time.")
        return values

    def set_speakers(self, instance, speaker_list):
        instance.speakers.clear()
        instance.speakers.set(get_entity(Speaker, speaker_info.get('href')) for speaker_info in speaker_list)
        return

    def create(self, validated_data):
        validated_data.pop('speakers')
        validated_data['track'] = get_entity(Track, self.initial_data.get('track', {}).get('href'))
        instance = super().create(validated_data=validated_data)
        self.set_speakers(instance, self.initial_data.get('speakers'))
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('speakers')
        validated_data['track'] = get_entity(Track, self.initial_data.get('track', {}).get('href'))
        instance = super().update(instance=instance, validated_data=validated_data)
        self.set_speakers(instance, self.initial_data.get('speakers'))
        return instance


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    events = get_entity_href_serializer(Event, many=True)
    capacity = serializers.SerializerMethodField()

    def get_capacity(self, obj: Session) -> int:
        '''

        :param obj: session object
        :return: total capacity of the session from all events
        '''
        return obj.get_capacity()

    class Meta:
        model = Session
        fields = (
            'href',
            'name',
            'events',
            'capacity',
        )
        extra_kwargs = {
            'href': {'lookup_field': 'id'},
        }


class CreateAndUpdateSessionSerializer(serializers.ModelSerializer):
    events = get_entity_href_serializer(Event, many=True)

    class Meta:
        model = Session
        fields = (
            'href',
            'name',
            'events',
        )
        extra_kwargs = {
            'href': {'lookup_field': 'id'},
        }

    def validate_events(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def set_events(self, instance, event_list):
        instance.events.clear()
        instance.events.set(get_entity(Event, event_info.get('href')) for event_info in event_list)

    def create(self, validated_data):
        validated_data.pop('events')
        instance = super().create(validated_data=validated_data)
        self.set_events(instance, self.initial_data.get('events'))
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('events')
        instance = super().update(instance=instance, validated_data=validated_data)
        self.set_events(instance, self.initial_data.get('events'))
        return instance


class AttendeeSerializer(serializers.Serializer):
    purchaser_email = serializers.EmailField()
    purchaser_first_name = serializers.CharField(max_length=100)
    purchaser_last_name = serializers.CharField(max_length=100)
    purchaser_phone_number = serializers.CharField(validators=[PhoneNumberValidator()])
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(validators=[PhoneNumberValidator()])
    country = serializers.CharField(max_length=100)
    birth_date = serializers.DateField()
    gender = serializers.CharField(max_length=10)
    occupation = serializers.CharField(max_length=100)
    marital_status = serializers.CharField(max_length=10)


class SessionPurchaseSerializer(serializers.Serializer):
    attendees = AttendeeSerializer(many=True)

    def validate_attendees(self, values):
        if not values:
            raise serializers.ValidationError("This field is required.")

        return values


class SpeakerSerializer(serializers.HyperlinkedModelSerializer):
    events = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj: Speaker):
        return obj.profile.get_full_name()

    def get_events(self, obj: Speaker):
        events = obj.speaker_events.all()
        return EventSerializer(events, many=True).data

    class Meta:
        model = Speaker
        fields = (
            'href',
            'name',
            'role',
            'events'
        )
        extra_kwargs = {
            'href': {'lookup_field': 'id'},
        }


class UserAndProfileSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(validators=[PhoneNumberValidator()])
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(Gender.choices, required=False, allow_null=True)
    occupation = serializers.CharField(max_length=100, required=False, allow_blank=True)
    marital_status = serializers.ChoiceField(MaritalStatus.choices, required=False, allow_null=True)


class CreateAndUpdateSpeakerSerializer(serializers.Serializer):
    profile = UserAndProfileSerializer()
    role = serializers.ChoiceField(Responsibility.choices)
