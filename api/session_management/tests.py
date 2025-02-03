from datetime import datetime, timedelta
from http import HTTPStatus

from rest_framework.test import APITestCase

from api.session_management.models import Event, Speaker
from api.utils.fakers import UserFactory, VenueFactory, TrackFactory, EventFactory, SpeakerFactory, SessionFactory


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


    def test_create_event(self):
        self.client.force_authenticate(self.admin)
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        with self.subTest('success'):
            response = self.client.post('/api/event/', {
                'track': self.example_track.id,
                'name': 'test event',
                'capacity': self.example_track.capacity - 2,
                'date': current_date,
                'start_time': current_time,
                'end_time': (current_datetime + timedelta(minutes=120)).time(),
            })
            self.assertEqual(response.status_code, HTTPStatus.CREATED)

        with self.subTest('failed - capacity not enough'):
            response = self.client.post('/api/event/', {
                'track': self.example_track.id,
                'name': 'test event',
                'capacity': self.example_track.capacity + 100,
                'date': current_date,
                'start_time': current_time,
                'end_time': (current_datetime + timedelta(minutes=120)).time(),
            })
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('capacity'),
                             "Capacity is greater than track capacity.")

        with self.subTest('failed - conflict track and datetime'):
            EventFactory(track=self.example_track, date=current_date,
                         start_time=(current_datetime - timedelta(minutes=480)).time(),
                         end_time=(current_datetime - timedelta(minutes=360)).time())
            for i in range(3):
                EventFactory(track=self.example_track, date=current_date,
                             start_time=(current_datetime + timedelta(minutes=120*i)).time(),
                             end_time=(current_datetime + timedelta(minutes=120*i+1)).time())

            response = self.client.post('/api/event/', {
                'track': self.example_track.id,
                'name': 'test event',
                'capacity': self.example_track.capacity,
                'date': current_date,
                'start_time': current_time,
                'end_time': (current_datetime + timedelta(minutes=120)).time(),
            })
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('main_error'), "Track already has event at this time, "
                                              "please choose different track or time.")

        with self.subTest('failed - bad request'):
            response = self.client.post('/api/event/', {
                'track': self.example_track.id,
                'name': 'test event',
                'date': current_date,
                'start_time': current_time,
                'end_time': (current_datetime + timedelta(minutes=120)).time(),
            })
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('capacity'),
                             "This field is required.")

        self.client.logout()
        with self.subTest('failed unauthorized'):
            response = self.client.post('/api/event/', {
                'track': self.example_track.id,
                'name': 'test event',
                'capacity': self.example_track.capacity - 2,
                'date': current_date,
                'start_time': current_time,
                'end_time': (current_datetime + timedelta(minutes=120)).time(),
            })
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
            response = self.client.get(f'/api/event/{sample_event.id+100}/')
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
        new_track = TrackFactory(venue=self.example_venue)
        for i in range(3):
            EventFactory(track=self.example_track, date=current_date,
                         start_time=(current_datetime + timedelta(minutes=120 * i)).time(),
                         end_time=(current_datetime + timedelta(minutes=120 * i + 1)).time())

        updated_data = {
            'track': new_track.id,
            'name': 'updated event',
            'capacity': new_track.capacity - 5,
            'date': current_date,
            'description': 'updated description',
            'start_time': (current_datetime + timedelta(minutes=120)).time(),
            'end_time': (current_datetime + timedelta(minutes=240)).time(),
        }
        with self.subTest('success'):

            response = self.client.put(f'/api/event/{sample_event.id}/', updated_data)
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('name'), 'updated event')

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
                'events': [event.id for event in Event.objects.all()[:2]],
                'speakers': [speaker.id for speaker in Speaker.objects.all()[:2]],
                'name': 'test session',
            })
            self.assertEqual(response.status_code, HTTPStatus.CREATED)

        with self.subTest('failed - bad request'):
            response = self.client.post('/api/session/', {
                'speakers': [speaker.id for speaker in Speaker.objects.all()[:2]],
                'name': 'test session',
            })
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        self.client.logout()
        with self.subTest('failed - unauthorized'):
            response = self.client.post('/api/session/', {
                'speakers': [speaker.id for speaker in Speaker.objects.all()[:2]],
                'name': 'test session',
            })
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
                'events': [event.id for event in Event.objects.all()[:2]],
                'speakers': [speaker.id for speaker in Speaker.objects.all()[:2]],
                'name': 'test session updated',
            })
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('name'), 'test session updated')

        with self.subTest('failed - bad request'):
            response = self.client.put(f'/api/session/{self.example_session.id}/', {
                'speakers': [speaker.id for speaker in Speaker.objects.all()[:2]],
                'name': 'test session',
            })
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(response_data.get('details', {}).get('field_errors', {}).get('events'),
                             'This field is required.')

        self.client.logout()
        with self.subTest('failed - unauthorized'):
            response = self.client.put(f'/api/session/{self.example_session.id}/', {
                'speakers': [speaker.id for speaker in Speaker.objects.all()[:2]],
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


