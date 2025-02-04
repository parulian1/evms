from datetime import datetime
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils.text import slugify
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins

from api.session_management.models import Event, Session, Attendee, Speaker
from api.session_management.serializers import EventSerializer, SessionSerializer, CreateAndUpdateSessionSerializer, \
    CreateAndUpdateEventSerializer, SessionPurchaseSerializer, CreateAndUpdateSpeakerSerializer, SpeakerSerializer
from api.utils.helpers import http_code_to_message
from api.utils.permissions import IsStaffOrAdmin, IsReadOnly


# Create your views here.
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CreateAndUpdateEventSerializer
        return self.serializer_class


class SessionViewSet(ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CreateAndUpdateSessionSerializer
        return self.serializer_class


class SessionPurchaseViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = SessionPurchaseSerializer

    def get_session(self):
        '''
        :return: session object based on session_pk in url
        '''
        try:
            return Session.objects.get(
                id=self.kwargs.get('session_pk')
            )
        except Session.DoesNotExist:
            raise Http404()

    def _find_duplicated_attendees_by_email(self, session, attendees):
        email_list = list(Attendee.objects.filter(
            session=session,
            user__email__in=[attendee.get('email') for attendee in attendees]
        ).distinct().values_list('user__email', flat=True))
        return email_list

    def _get_attendee_count_of_session(self, session):
        return session.attendees.count()

    def is_attendee_count_exceeded(self, session, attendees):
        return (self._get_attendee_count_of_session(session) + len(attendees)) > session.get_capacity()

    def is_valid(self, session, attendees):
        if len(self._find_duplicated_attendees_by_email(session, attendees)):
            return False
        if self.is_attendee_count_exceeded(session, attendees):
            return False
        return True

    def create(self, request, *args, **kwargs):
        from api.users.models import Profile
        session = self.get_session()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_year = datetime.now().year
        attendees = serializer.validated_data.get('attendees')
        if not self.is_valid(session, attendees):
            duplicated_attendees = self._find_duplicated_attendees_by_email(session, attendees)
            main_error = ''
            if len(duplicated_attendees):
                joined_duplicated_attendee_emails = ', '.join(duplicated_attendees)
                main_error = (f'Attendee with this email ({joined_duplicated_attendee_emails}) already '
                              f'register into this session.')
            if self.is_attendee_count_exceeded(session, attendees):
                main_error = 'Attendee registered was exceeded the capacity of this session.'
            return Response(
                data={
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "type": "ValidationError",
                    "message": http_code_to_message[status.HTTP_400_BAD_REQUEST],
                    "details": {
                        "field_errors": {},
                        "main_error": main_error
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            for attendee in attendees:
                user, is_created = get_user_model().objects.get_or_create(email=attendee.get('email'))
                user.first_name = attendee.get('first_name')
                user.last_name = attendee.get('last_name')
                user.phone_number = attendee.get('phone_number')
                user.is_guest = True
                if is_created:
                    user.set_password(slugify(f'{session.name[:5]}-{current_year}'))
                user.save()
                profile, is_created = Profile.objects.get_or_create(user=user)
                if is_created:
                    profile.country = attendee.get('country')
                profile.birth_date = attendee.get('birth_date')
                profile.gender = attendee.get('gender')
                profile.occupation = attendee.get('occupation')
                profile.marital_status = attendee.get('marital_status')
                profile.save()
                Attendee.objects.create(session=session, user=user,
                                        purchaser_email=attendee.get('purchaser_email'),
                                        purchaser_first_name=attendee.get('purchaser_first_name'),
                                        purchaser_last_name=attendee.get('purchaser_last_name'),
                                        purchaser_phone_number=attendee.get('purchaser_phone_number'))

            return Response(status=status.HTTP_201_CREATED)


class SpeakerViewSet(ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    permission_classes = [IsStaffOrAdmin | (~IsStaffOrAdmin & IsReadOnly)]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CreateAndUpdateSpeakerSerializer
        return self.serializer_class

    def generate_profile(self, speaker: Speaker, profile_info: dict, year: int):
        from api.users.models import Profile
        if speaker:
            profile = speaker.profile
            user = profile.user
        else:
            user, is_created = get_user_model().objects.get_or_create(email=profile_info.get('email'))
            profile, is_profile_created = Profile.objects.get_or_create(user=user)
            if is_created:
                user.set_password(slugify(f'{year}{user.email}'))
        user.first_name = profile_info.get('first_name')
        user.last_name = profile_info.get('last_name')
        user.phone_number = profile_info.get('phone_number')
        user.is_guest = True
        user.save()
        profile.country = profile_info.get('country')
        profile.birth_date = profile_info.get('birth_date')
        profile.gender = profile_info.get('gender')
        profile.occupation = profile_info.get('occupation')
        profile.marital_status = profile_info.get('marital_status')
        profile.save()
        return profile

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        today_year = datetime.now().year
        profile_info = serializer.validated_data.get('profile')
        role = serializer.validated_data.get('role')
        profile = self.generate_profile(speaker=None, profile_info=profile_info, year=today_year)
        speaker, is_created = Speaker.objects.get_or_create(profile=profile)
        speaker.role = role
        speaker.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        today_year = datetime.now().year
        profile_info = serializer.validated_data.get('profile')
        role = serializer.validated_data.get('role')
        speaker = self.get_object()
        speaker.role = role
        speaker.save()
        self.generate_profile(speaker=speaker, profile_info=profile_info, year=today_year)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_speaker_attached_to_events = instance.speaker_events.exists()
        if is_speaker_attached_to_events:
            return Response({
                "status_code": status.HTTP_409_CONFLICT,
                "type": "ValidationError",
                "message": http_code_to_message[status.HTTP_409_CONFLICT],
                "details": {
                    "field_errors": '',
                    "main_error": "Failed to delete speaker because it is attached to events. Please detach it first."
                }
            }, status=status.HTTP_409_CONFLICT)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)