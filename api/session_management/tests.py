from datetime import datetime, timedelta
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from faker import Faker

from api.session_management.models import Event, Speaker
from api.utils.fakers import UserFactory, VenueFactory, TrackFactory, EventFactory, SpeakerFactory, SessionFactory, \
    UserProfileFactory


# Create your tests here.
class EventAndSessionApiTests(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True, is_superuser=True, is_active=True)
        self.non_admin = UserFactory(is_staff=False, is_superuser=False, is_active=True)
        self.example_venue = VenueFactory()
        self.example_track = TrackFactory(venue=self.example_venue)
        for _ in range(2):
            EventFactory(track=self.example_track)
        for _ in range(4):
            SpeakerFactory()
        self.example_session = SessionFactory()

    def generate_entity_data(self, obj):
        entity_data = {
            'href': f'http://testserver/api/{obj._meta.model_name}/{obj.id}/'
        }
        if hasattr(obj, 'name'):
            entity_data['name'] = obj.name
        return entity_data

    def test_create_event(self):
        self.client.force_authenticate(self.admin)
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        request_data = {
            'track': self.generate_entity_data(self.example_track),
            'name': 'test event',
            'capacity': self.example_track.capacity - 2,
            'speakers': [self.generate_entity_data(speaker) for speaker in Speaker.objects.all()[:2]],
            'date': current_date.isoformat(),
            'start_time': current_time.isoformat(),
            'end_time': (current_datetime + timedelta(minutes=120)).time().isoformat(),
        }
        with self.subTest('success'):
            response = self.client.post('/api/event/', request_data, format='json')
            self.assertEqual(response.status_code, HTTPStatus.CREATED)

        with self.subTest('failed - capacity not enough'):
            request_data['capacity'] = self.example_track.capacity + 100
            response = self.client.post('/api/event/', request_data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('capacity'),
                             "Capacity is greater than track capacity.")

        with self.subTest('failed - conflict track and date - time'):
            EventFactory(track=self.example_track, date=current_date,
                         start_time=(current_datetime - timedelta(minutes=480)).time(),
                         end_time=(current_datetime - timedelta(minutes=360)).time())

            for i in range(3):
                EventFactory(track=self.example_track, date=current_date,
                             start_time=(current_datetime + timedelta(minutes=120 * i)).time(),
                             end_time=(current_datetime + timedelta(minutes=120 * i + 1)).time())
            request_data['capacity'] = self.example_track.capacity
            response = self.client.post('/api/event/', request_data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('track'),
                             "Track already has event at this time, "
                             "please choose different track or time.")

        with self.subTest('failed - conflict speaker and date - time'):
            other_event = EventFactory(track=self.example_track, date=current_date,
                                       start_time=(current_datetime - timedelta(minutes=480)).time(),
                                       end_time=(current_datetime - timedelta(minutes=360)).time())
            speaker_a = SpeakerFactory()
            other_event.speakers.add(speaker_a)
            other_event.save()
            other_track = TrackFactory(venue=self.example_venue)
            request_data['track'] = self.generate_entity_data(other_track)
            for i in range(3):
                EventFactory(track=self.example_track, date=current_date,
                             start_time=(current_datetime + timedelta(minutes=120 * i)).time(),
                             end_time=(current_datetime + timedelta(minutes=120 * i + 1)).time())
            request_data['capacity'] = self.example_track.capacity
            request_data['speakers'].append(self.generate_entity_data(speaker_a))
            response = self.client.post('/api/event/', request_data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('speakers'),
                             "Some of the speaker(s) already has event at this time, "
                             "please choose different speaker(s) or time.")

        with self.subTest('failed - bad request'):
            request_data.pop('capacity')
            response = self.client.post('/api/event/', request_data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('capacity'),
                             "This field is required.")

        self.client.logout()
        with self.subTest('failed unauthorized'):
            response = self.client.post('/api/event/', request_data, format='json')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_event_detail(self):
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        sample_event = EventFactory(track=self.example_track, date=current_date,
                                    start_time=(current_datetime - timedelta(minutes=480)).time(),
                                    end_time=(current_datetime - timedelta(minutes=360)).time())
        with self.subTest('success'):
            response = self.client.get(f'/api/event/{sample_event.id}/')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('name'), sample_event.name)

        with self.subTest('failed - not found'):
            response = self.client.get(f'/api/event/{sample_event.id + 100}/')
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_event_list(self):
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        for i in range(3):
            EventFactory(track=self.example_track, date=current_date,
                         start_time=(current_datetime + timedelta(minutes=120 * i)).time(),
                         end_time=(current_datetime + timedelta(minutes=120 * i + 1)).time())
        with self.subTest('success'):
            response = self.client.get('/api/event/')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertTrue(len(response_data))

    def test_update_event(self):
        self.client.force_authenticate(self.admin)
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        sample_event = EventFactory(track=self.example_track, date=current_date,
                                    start_time=(current_datetime - timedelta(minutes=360)).time(),
                                    end_time=(current_datetime - timedelta(minutes=240)).time())
        EventFactory(track=self.example_track, date=current_date,
                     start_time=(current_datetime - timedelta(minutes=360)).time(),
                     end_time=(current_datetime - timedelta(minutes=240)).time())
        for i in range(3):
            EventFactory(track=self.example_track, date=current_date,
                         start_time=(current_datetime + timedelta(minutes=120 * i)).time(),
                         end_time=(current_datetime + timedelta(minutes=120 * i + 1)).time())

        sample_event.speakers.clear()
        sample_event.speakers.add(SpeakerFactory())
        sample_event.speakers.add(SpeakerFactory())
        sample_event.save()
        new_track = TrackFactory(venue=self.example_venue)
        updated_data = {
            'track': self.generate_entity_data(new_track),
            'speakers': [self.generate_entity_data(speaker) for speaker in sample_event.speakers.all()],
            'name': 'updated event',
            'capacity': new_track.capacity - 5,
            'date': current_date.isoformat(),
            'description': 'updated description',
            'start_time': (current_datetime + timedelta(minutes=120)).time().isoformat(),
            'end_time': (current_datetime + timedelta(minutes=240)).time().isoformat(),
        }
        with self.subTest('success'):
            response = self.client.put(f'/api/event/{sample_event.id}/', updated_data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('name'), 'updated event')

        with (self.subTest('failed - conflict speaker and date - time')):
            other_event = Event.objects.filter(
                date=current_date,
                start_time=(current_datetime - timedelta(minutes=360)).time(),
                end_time=(current_datetime - timedelta(minutes=240)).time()
            ).exclude(id=sample_event.id).first()
            speaker_already_in_event = other_event.speakers.first()
            updated_data['speakers'].append(self.generate_entity_data(speaker_already_in_event))
            response = self.client.put(f'/api/event/{sample_event.id}/', updated_data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('speakers'),
                             "Some of the speaker(s) already has event at this time, "
                             "please choose different speaker(s) or time.")

        with self.subTest('failed - bad request'):
            updated_data.pop('track')
            response = self.client.put(f'/api/event/{sample_event.id}/', updated_data)
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('track'),
                             "This field is required.")

        self.client.logout()
        with self.subTest('failed unauthorized'):
            response = self.client.put(f'/api/event/{sample_event.id}/', updated_data)
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_delete_event(self):
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        sample_event = EventFactory(track=self.example_track, date=current_date,
                                    start_time=(current_datetime - timedelta(minutes=360)).time(),
                                    end_time=(current_datetime - timedelta(minutes=240)).time())
        with self.subTest('failed unauthorized'):
            response = self.client.delete(f'/api/event/{sample_event.id}/')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.delete(f'/api/event/{sample_event.id}/')
            self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_create_session(self):
        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.post('/api/session/', {
                'events': [self.generate_entity_data(event) for event in Event.objects.all()[:2]],
                'name': 'test session',
            }, format='json')
            self.assertEqual(response.status_code, HTTPStatus.CREATED)

        with self.subTest('failed - bad request'):
            response = self.client.post('/api/session/', {
                'speakers': [self.generate_entity_data(speaker) for speaker in Speaker.objects.all()[:2]],
                'name': 'test session',
            }, format='json')
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        self.client.logout()
        with self.subTest('failed - unauthorized'):
            response = self.client.post('/api/session/', {
                'speakers': [speaker.id for speaker in Speaker.objects.all()[:2]],
                'name': 'test session',
            }, format='json')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_session_list(self):
        for _ in range(3):
            SessionFactory()
        with self.subTest('success'):
            response = self.client.get('/api/session/')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertTrue(len(response_data))

    def test_get_session_detail(self):
        other_track = TrackFactory(capacity=100, venue=self.example_venue)
        EventFactory(track=other_track)
        example_session = SessionFactory()
        with self.subTest('success'):
            response = self.client.get(f'/api/session/{example_session.id}/')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertTrue(response_data.get('capacity'))

    def test_update_session(self):
        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.put(f'/api/session/{self.example_session.id}/', {
                'events': [self.generate_entity_data(event) for event in Event.objects.all()[:2]],
                'name': 'test session updated',
            }, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('name'), 'test session updated')

        with self.subTest('failed - bad request'):
            response = self.client.put(f'/api/session/{self.example_session.id}/', {
                'name': 'test session',
            })
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('events'),
                             'This field is required.')

        self.client.logout()
        with self.subTest('failed - unauthorized'):
            response = self.client.put(f'/api/session/{self.example_session.id}/', {
                'speakers': [self.generate_entity_data(speaker) for speaker in Speaker.objects.all()[:2]],
                'name': 'test session',
            })
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_delete_session(self):
        with self.subTest('failed - unauthorized'):
            response = self.client.delete(f'/api/session/{self.example_session.id}/')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.delete(f'/api/session/{self.example_session.id}/')
            self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        with self.subTest('failed - not found'):
            response = self.client.delete('/api/session/500/')
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class SessionPurchaseApiTests(APITestCase):
    def setUp(self):
        self.example_venue = VenueFactory()
        self.example_track = TrackFactory(venue=self.example_venue)
        for _ in range(3):
            EventFactory(track=self.example_track)
        self.sample_session = SessionFactory()
        self.sample_session.events.set(Event.objects.all())
        for _ in range(10):
            UserProfileFactory()

    def test_purchase(self):
        first_user = get_user_model().objects.first()
        data = {
            'attendees': [{
                'purchaser_email': first_user.email,
                'purchaser_first_name': first_user.first_name,
                'purchaser_last_name': first_user.last_name,
                'purchaser_phone_number': first_user.phone_number,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'country': 'Indonesia',
                'birth_date': '1990-01-01',
                'gender': 'male',
                'occupation': 'student',
                'marital_status': 'single',
            } for user in get_user_model().objects.exclude(id=first_user.id)]
        }
        with self.subTest('success'):
            response = self.client.post(reverse("purchase-list", kwargs={"session_id": self.sample_session.id}),
                                        data, format='json')
            self.assertEqual(response.status_code, HTTPStatus.CREATED)
        other_track = TrackFactory(venue=self.example_venue)
        for _ in range(3):
            EventFactory(track=other_track, capacity=2)

        other_session = SessionFactory()
        other_session.events.set(Event.objects.exclude(sessions__in=[self.sample_session.id]))
        with self.subTest('failed - session capacity not enough'):
            response = self.client.post(f'/api/session/{other_session.id}/purchase/', data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('main_error', {}),
                             "Attendee registered was exceeded the capacity of this session.")

        with self.subTest('failed - bad request'):
            data['attendees'] = [{
                'purchaser_email': first_user.email,
                'purchaser_first_name': first_user.first_name,
                'purchaser_last_name': first_user.last_name,
                'purchaser_phone_number': first_user.phone_number,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'country': 'Indonesia',
                'birth_date': '1990-01-01',
                'gender': 'male',
                'occupation': 'student',
                'marital_status': 'single',
            } for user in get_user_model().objects.exclude(id=first_user.id)]
            response = self.client.post(f'/api/session/{other_session.id}/purchase/', data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertIsNotNone(response_data.get('details', {}).get('field_errors', {}).get('attendees'))


class SpeakerApiTests(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True, is_superuser=True, is_active=True)
        self.faker = Faker('id_ID')
        self.email = self.faker.email()
        self.first_name = self.faker.first_name()
        self.last_name = self.faker.last_name()
        self.phone_number = self.faker.phone_number()
        self.country = self.faker.country()
        self.birth_date = self.faker.date_of_birth()
        self.gender = self.faker.random_element(elements=('male', 'female'))
        self.occupation = self.faker.job()
        self.marital_status = self.faker.random_element(elements=('single', 'married'))
        self.example_speaker = SpeakerFactory()

    def test_create_speaker(self):
        self.client.force_authenticate(self.admin)
        speaker_data = {
            'profile': {
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'phone_number': self.phone_number,
                'country': self.country,
                'birth_date': self.birth_date.isoformat(),
                'gender': self.gender,
                'occupation': self.occupation,
                'marital_status': self.marital_status,
            },
            'role': 'participant',
        }
        with self.subTest('success'):
            response = self.client.post('/api/speaker/', speaker_data, format='json')
            self.assertEqual(response.status_code, HTTPStatus.CREATED)

        with self.subTest('failed - bad request'):
            response = self.client.post('/api/speaker/', {
                'profile': {
                    'email': self.email,
                    'first_name': self.first_name,
                    'last_name': self.last_name,
                    'phone_number': self.phone_number,
                    'country': self.country,
                    'birth_date': self.birth_date.isoformat(),
                    'gender': self.gender,
                    'occupation': self.occupation,
                    'marital_status': self.marital_status,
                },
            }, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('role'),
                             'This field is required.')

        self.client.logout()
        with self.subTest('failed - unauthorized'):
            response = self.client.post('/api/speaker/', speaker_data, format='json')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_update_speaker(self):
        self.client.force_authenticate(self.admin)
        speaker_data = {
            'profile': {
                'email': self.example_speaker.profile.user.email,
                'first_name': 'updated first name',
                'last_name': self.last_name,
                'phone_number': self.phone_number,
                'country': self.country,
                'birth_date': self.birth_date.isoformat(),
                'gender': self.gender,
                'occupation': self.occupation,
                'marital_status': self.marital_status,
            },
            'role': 'participant',
        }
        with self.subTest('success'):
            response = self.client.put(f'/api/speaker/{self.example_speaker.id}/', speaker_data, format='json')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('profile', {}).get('first_name'), 'updated first name')

        with self.subTest('failed - bad request'):
            speaker_data.pop('role')
            response = self.client.put(f'/api/speaker/{self.example_speaker.id}/', speaker_data, format='json')
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        self.client.logout()
        with self.subTest('failed - unauthorized'):
            response = self.client.put(f'/api/speaker/{self.example_speaker.id}/', speaker_data, format='json')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_speaker(self):
        with self.subTest('list'):
            response = self.client.get('/api/speaker/')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertTrue(len(response_data))

        with self.subTest('detail'):
            response = self.client.get(f'/api/speaker/{self.example_speaker.id}/')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('role'), self.example_speaker.role)

        with self.subTest('detail - not found'):
            response = self.client.get('/api/speaker/100/')
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_speaker(self):
        example_event = EventFactory()
        example_event.speakers.add(self.example_speaker)
        example_event.save()

        with self.subTest('failed - unauthorized'):
            response = self.client.delete(f'/api/speaker/{self.example_speaker.id}/')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        self.client.force_authenticate(self.admin)
        with self.subTest('failed - conflict'):
            response = self.client.delete(f'/api/speaker/{self.example_speaker.id}/')
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.CONFLICT)
            self.assertIsNotNone(response_data.get('details', {}).get('main_error'))

        example_event.speakers.remove(self.example_speaker)
        example_event.save()
        with self.subTest('success'):
            response = self.client.delete(f'/api/speaker/{self.example_speaker.id}/')
            self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

