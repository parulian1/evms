from django.db.models import Q
from rest_framework import serializers

from api.session_management.models import Event, Session, Speaker
from api.track.models import Track
from api.track.serializers import TrackSerializer
from api.utils.choices import Gender, MaritalStatus, Responsibility
from api.utils.validators import PhoneNumberValidator


class EventSerializer(serializers.ModelSerializer):
    track = TrackSerializer()
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
        fields = '__all__'


class CreateAndUpdateEventSerializer(serializers.ModelSerializer):
    track = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all())
    speakers = serializers.PrimaryKeyRelatedField(
        queryset=Speaker.objects.all(),
        many=True
    )

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

    def validate_track(self, value):
        date = self.initial_data.get('date')
        track_id = value
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
        if not values:
            raise serializers.ValidationError("This field is required.")
        else:
            date = self.initial_data.get('date')
            query  = Event.objects.filter(
                Q(date=date),
                Q(
                    Q(start_time__gte=self.initial_data.get('end_time')) |
                    Q(end_time__gte=self.initial_data.get('start_time'))
                ),
                Q(speakers__in=values)
            ).distinct()
            if self.instance:
                query = query.exclude(id=self.instance.id)
            existing_events_in_time_occurrence = query.exists()
            if existing_events_in_time_occurrence:
                raise serializers.ValidationError("Some of the speaker(s) already has event at this time, "
                                                  "please choose different speaker(s) or time.")
        return values


class SessionSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True)
    capacity = serializers.SerializerMethodField()

    def get_capacity(self, obj: Session) -> int:
        '''

        :param obj: session object
        :return: total capacity of the session from all events
        '''
        return obj.get_capacity()

    class Meta:
        model = Session
        fields = '__all__'


class CreateAndUpdateSessionSerializer(serializers.ModelSerializer):
    events = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        many=True
    )

    class Meta:
        model = Session
        fields = '__all__'

    def validate_events(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value


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


class SpeakerSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()

    def get_events(self, obj: Speaker):
        events = obj.speaker_events.all()
        return EventSerializer(events, many=True).data

    class Meta:
        model = Speaker
        fields = '__all__'


class UserAndProfileSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(validators=[PhoneNumberValidator()])
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(Gender.choices, required=False, allow_null=True)
    occupation  = serializers.CharField(max_length=100, required=False, allow_blank=True)
    marital_status = serializers.ChoiceField(MaritalStatus.choices, required=False, allow_null=True)


class CreateAndUpdateSpeakerSerializer(serializers.Serializer):
    profile = UserAndProfileSerializer()
    role = serializers.ChoiceField(Responsibility.choices)
