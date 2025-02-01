from http import HTTPStatus

from django.test import TestCase
from rest_framework.test import APITestCase

from api.utils.fakers import UserFactory, VenueFactory, TrackFactory


# Create your tests here.
class VenueTrackApiTests(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True, is_superuser=True, is_active=True)
        self.admin_pass = 'p@ssw0rd'
        self.admin.set_password(self.admin_pass)
        self.admin.save()
        self.non_admin = UserFactory(is_staff=False, is_superuser=False, is_active=True)
        self.non_admin.set_password(self.admin_pass)
        self.non_admin.save()
        self.example_venue = VenueFactory()
        self.example_track = TrackFactory()

    def test_create_venue(self):
        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.post(
                '/api/venue/',
                {
                    'name': 'test venue',
                    'location': 'test address',
                    'description': 'test venue description',
                    'is_available': True
                },
            )
            self.assertEqual(response.status_code, HTTPStatus.CREATED)

        with self.subTest('failed bad request'):
            response = self.client.post(
                '/api/venue/',
                {
                    'name': 'test venue',
                    'description': 'test venue description',
                },
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        self.client.logout()
        with self.subTest('failed forbidden'):
            self.client.force_authenticate(self.non_admin)
            response = self.client.post(
                '/api/venue/',
                {
                    'name': 'test venue',
                    'location': 'test address',
                    'description': 'test venue description',
                },
            )
            self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        self.client.logout()
        with self.subTest('failed unauthorized'):
            response = self.client.post(
                '/api/venue/',
                {
                    'name': 'test venue',
                    'location': 'test address',
                    'description': 'test venue description',
                },
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_update_venue(self):
        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.put(
                f'/api/venue/{self.example_venue.id}/',
                {
                    'name': 'updated venue',
                    'location': 'updated address',
                    'description': 'updated venue description',
                    'is_available': True
                },
            )
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('name'), 'updated venue')

        self.client.logout()
        with self.subTest('failed unauthorized'):
            response = self.client.put(
                f'/api/venue/{self.example_venue.id}/',
                {
                    'name': 'updated venue',
                    'location': 'updated address',
                    'description': 'updated venue description',
                    'is_available': True
                },
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        with self.subTest('failed - not found'):
            self.client.force_authenticate(self.admin)
            response = self.client.put(
                f'/api/venue/200/',
                {
                    'name': 'updated venue',
                    'location': 'updated address',
                    'description': 'updated venue description',
                    'is_available': True
                },
            )
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_venue_list(self):
        response = self.client.get(
            '/api/venue/'
        )
        response_data = response.json()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsNotNone(response_data)

    def test_venue_details(self):
        response = self.client.get(
            f'/api/venue/{self.example_venue.id}/'
        )
        response_data = response.json()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response_data.get('name'), self.example_venue.name)

    def test_venue_delete(self):
        with self.subTest('failed unauthorized'):
            response = self.client.delete(
                f'/api/venue/{self.example_venue.id}/'
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.delete(
                f'/api/venue/{self.example_venue.id}/'
            )
            self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_create_track(self):
        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.post(
                f'/api/track/',
                {
                    'venue': self.example_venue.id,
                    'name': 'test track',
                    'description': 'test track description',
                    'capacity': 100,
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.CREATED)

        with self.subTest('venue not found - bad request'):
            response = self.client.post(
                f'/api/track/',
                {
                    'venue': 100,
                    'name': 'test track',
                    'description': 'test track description',
                    'capacity': 100,
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        #
        self.client.force_authenticate(self.non_admin)
        with self.subTest('forbidden'):

            response = self.client.post(
                f'/api/track/',
                {
                    'venue': 100,
                    'name': 'test track',
                    'description': 'test track description',
                    'capacity': 100,
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        self.client.logout()
        with self.subTest('unauthorized'):
            response = self.client.post(
                f'/api/track/',
                {
                    'venue': 100,
                    'name': 'test track',
                    'description': 'test track description',
                    'capacity': 100,
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_update_track(self):
        self.client.force_authenticate(self.admin)
        with self.subTest('success'):
            response = self.client.put(
                f'/api/track/{self.example_track.id}/',
                {
                    'venue': self.example_venue.id,
                    'name': 'test track',
                    'description': 'test track description',
                    'capacity': 100,
                }
            )
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response_data.get('name'), 'test track')
            self.assertEqual(response_data.get('venue'), self.example_venue.id)

        with self.subTest('venue not found - bad request'):
            response = self.client.put(
                f'/api/track/{self.example_track.id}/',
                {
                    'venue': 100,
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        self.client.logout()
        self.client.force_authenticate(self.non_admin)
        with self.subTest('forbidden'):

            response = self.client.put(
                f'/api/track/{self.example_track.id}/',
                {
                    'venue': 100,
                    'name': 'test track',
                    'description': 'test track description',
                    'capacity': 100,
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        self.client.logout()
        with self.subTest('unauthorized'):
            response = self.client.put(
                f'/api/track/{self.example_track.id}/',
                {
                    'venue': 100,
                    'name': 'test track',
                    'description': 'test track description',
                    'capacity': 100,
                }
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_delete_track(self):
        with self.subTest('failed unauthorized'):
            response = self.client.delete(
                f'/api/track/{self.example_track.id}/',
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        self.client.force_authenticate(self.admin)
        with self.subTest('failed - not found'):
            response = self.client.delete(
                '/api/track/200/',
            )
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        with self.subTest('success'):
            response = self.client.delete(
                f'/api/track/{self.example_track.id}/',
            )
            self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
