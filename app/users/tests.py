from http import HTTPStatus

from rest_framework.test import APITestCase

from app.utils.fakers import UserFactory, UserProfileFactory


# Create your tests here.
class UserApiTests(APITestCase):
    def setUp(self):
        self.staff_email = 'evmsstaff@gmail.com'
        self.staff_pass = '3vmsst@ff_p@55'
        self.customer_email = 'emailtest@gmail.com'
        self.customer_pass = 'customerp@ss'
        self.staff2_password = '3vmsst@ff_p@552'
        self.customer2_password = 'customerp@ss2'
        self.staff2 = UserFactory(is_active=True)
        self.staff2.set_password(self.staff2_password)
        self.staff2.save()
        UserProfileFactory(user=self.staff2)
        self.customer2 = UserFactory(password=self.customer2_password, is_guest=True, is_active=True)
        self.customer2.set_password(self.customer2_password)
        self.customer2.save()

    def test_create_users(self):
        with self.subTest('staff registration'):
            with self.subTest('success'):
                response = self.client.post(
                    '/users/register/',
                    {
                        'email': self.staff_email, 'password': self.staff_pass, 'first_name': 'admin1',
                        'last_name': 'admin1'
                    },
                )
                self.assertEqual(response.status_code, HTTPStatus.CREATED)

            with self.subTest('failed'):
                response = self.client.post(
                    '/users/register/',
                    {
                        'email': self.staff_email, 'password': self.staff_pass, 'first_name': 'admin1'
                    },
                )
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        with self.subTest('customer registration'):
            with self.subTest('success'):
                response = self.client.post(
                    '/users/register/',
                    {
                        'email': self.customer_email, 'password': self.customer_pass, 'first_name': 'customer1',
                        'last_name': 'customer last name', 'phone_number': '0123456789', 'is_guest': True
                    },
                )
                self.assertEqual(response.status_code, HTTPStatus.CREATED)

            with self.subTest('failed'):
                response = self.client.post(
                    '/users/register/',
                    {
                        'email': self.customer_email, 'password': self.customer_pass, 'first_name': 'customer1'
                    },
                )
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_login(self):
        with self.subTest('success'):
            response = self.client.post(
                '/users/login/',
                data={'email': self.staff2.email, 'password': self.staff2_password}
            )
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIsNotNone(response_data.get('access'))


        with self.subTest('failed'):
            response = self.client.post(
                '/users/login/',
                {'email': self.customer_email, 'password': self.customer_pass}
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_retrieve_user_profile(self):
        with self.subTest('success'):
            self.client.force_authenticate(user=self.staff2)
            response = self.client.get(
                '/users/profile/',
            )
            response_data = response.json()
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIsNotNone(response_data.get('profile'))
