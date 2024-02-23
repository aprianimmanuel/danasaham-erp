from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from django_otp.plugins.otp_email.models import EmailDevice  # noqa
from django_otp import devices_for_user  # noqa

User = get_user_model()
CREATE_USER_URL = reverse('user:create')
TOKEN_OBTAIN_URL = reverse('user:login')
MANAGE_USER_URL = reverse('user:me')


class PublicUserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch('django_otp.plugins.otp_email.models.EmailDevice.verify_token')
    @patch('django_otp.devices_for_user')
    def test_create_user_success(
            self,
            mocked_devices_for_user,
            mocked_verify_token):
        """
        Test creating a new user with a mocked OTP email setup.
        """
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss123',
            'password2': 'Testp@ss123',
            'otp': '123456'  # Assuming OTP is required for the test
        }

        # Mocking the verify_token method to always return True
        mocked_verify_token.return_value = True

        # Preparing a mock device to return for devices_for_user
        mock_device = EmailDevice(user_id=1, confirmed=False)
        mocked_devices_for_user.return_value = [mock_device]

        response = self.client.post(CREATE_USER_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data['email']).exists())

        # Verifying that the mocked methods were called as expected
        mocked_devices_for_user.assert_called_once()
        mocked_verify_token.assert_called_once_with('123456')

        user = User.objects.get(email=data['email'])
        self.assertTrue(user.email_verified)

    def test_password_too_short_error(self):
        """Test creating a user with a password that is too short"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'pw',
            'password2': 'pw'
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_create_user_invalid_data(self):
        """Test creating a new user with invalid data"""
        invalid_data = [
            {'email': '',
             'username': 'testuser',
             'password': 'Testp@ss!23',
             'password2': 'Testp@ss!23'},
            {'email': 'invalidemail',
             'username': 'testuser',
             'password': 'Testp@ss!23',
             'password2': 'Testp@ss!23'},
            {'email': 'test@example.com',
             'username': '',
             'password': 'Testp@ss!23',
             'password2': 'Testp@ss!23'},
            {'email': 'test@example.com',
             'username': 'testuser',
             'password': '',
             'password2': ''},
            {'email': 'test@example.com',
             'username': 'test_user#1',
             'password': 'Testp@ss!23',
             'password2': 'Testp@ss!23'},
        ]

        for data in invalid_data:
            response = self.client.post(CREATE_USER_URL, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        for key in data:
            if key in response.data:
                self.assertIn(key, response.data)

            user_exists = User.objects.filter(email=data.get('email', '')).exists()  # noqa
            self.assertFalse(user_exists, f"User should not be created with data: {data}")  # noqa

    def test_create_user_duplicate_fields(self):
        """Test creating a new user with duplicate email or username"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23'
        }
        create_user_response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)  # noqa

        duplicate_email_data = {
            'email': 'test@example.com',
            'username': 'testuser2',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23'
        }
        duplicate_email_response = self.client.post(CREATE_USER_URL,
                                                    duplicate_email_data)
        self.assertEqual(duplicate_email_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', duplicate_email_response.data)

        duplicate_username_data = {
            'email': 'test1@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23'
        }
        duplicate_username_response = self.client.post(CREATE_USER_URL,
                                                       duplicate_username_data)
        self.assertEqual(duplicate_username_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', duplicate_username_response.data)

    def test_create_user_missing_required_fields(self):
        """Test creating a new user with missing required fields"""
        data = {
            'email': '',
            'username': '',
            'password': '',
            'password2': ''
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_password_mismatch(self):
        """Test creating a new user with password confirmation mismatch"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!24'
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_email_verification_success(self):
        """Test email verification process"""
        # Assuming user creation here and EmailDevice setup
        # Assuming 'verify_email' is the URL name for email verification endpoint
        VERIFY_EMAIL_URL = reverse('user:verify_email')
        data = {
            'email': self.user.email,
            'otp': '123456'  # Assuming this is the correct OTP for the test
        }
        response = self.client.post(VERIFY_EMAIL_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)


class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()  # Instantiate the Django REST Framework's APIClient  # noqa
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23'
        )
        self.client.force_authenticate(user=self.user)  # Force authenticate the user for subsequent requests  # noqa
