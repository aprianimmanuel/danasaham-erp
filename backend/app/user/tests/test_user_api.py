from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from django_otp.plugins.otp_email.models import EmailDevice  # noqa
from django_otp import devices_for_user  # noqa
import uuid


User = get_user_model()
CREATE_USER_URL = reverse('user:create')
TOKEN_OBTAIN_URL = reverse('user:login')
MANAGE_USER_URL = reverse('user:me')

class MockQuerySet:
    def __init__(self, *args):
        self._items = list(args)

    def filter(self, **kwargs):
        filtered_items = [item for item in self._items if all(getattr(item, k) == v for k, v in kwargs.items())]
        return MockQuerySet(*filtered_items)

    def all(self):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def last(self):
        return self._items[-1] if self._items else None

    def exists(self):
        return bool(self._items)

    def count(self):
        return len(self._items)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class PublicUserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch('django_otp.devices_for_user')
    def test_create_user_success(self, mocked_devices_for_user):
        """
        Test creating a new user with a mocked OTP email setup.
        """
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23',
            'otp': '123456'
        }

        # Set up MagicMock to simulate QuerySet behavior
        mock_device = MagicMock(spec=EmailDevice)
        mock_device.verify_token.return_value = True
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = [mock_device]  # Simulate filter returning a list
        
        mocked_devices_for_user.return_value = mock_queryset  # Return the mock queryset

        response = self.client.post(CREATE_USER_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=data['email'])
        self.assertTrue(user.email_verified)

        # Ensure the mocks were called as expected
        mocked_devices_for_user.assert_called_once_with(user, confirmed=False)
        mock_queryset.filter.assert_called_with(emaildevice_isnull=False)
        mock_device.verify_token.assert_called_once_with('123456')

    def test_password_too_short_error(self):
        """Test creating a user with a password that is too short"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'pw',
            'password2': 'pw',
            'otp': '123456'
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
             'password2': 'Testp@ss!23',
             'otp': '123456'},
            {'email': 'invalidemail',
             'username': 'testuser',
             'password': 'Testp@ss!23',
             'password2': 'Testp@ss!23',
             'otp': '123456'},
            {'email': 'test@example.com',
             'username': '',
             'password': 'Testp@ss!23',
             'password2': 'Testp@ss!23',
             'otp': '123456'},
            {'email': 'test@example.com',
             'username': 'testuser',
             'password': '',
             'password2': '',
             'otp': '123456'},
            {'email': 'test@example.com',
             'username': 'test_user#1',
             'password': 'Testp@ss!23',
             'password2': 'Testp@ss!23',
             'otp': '123456'},
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
            'password2': 'Testp@ss!23',
            'otp': '123456'
        }
        create_user_response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)  # noqa

        duplicate_email_data = {
            'email': 'test@example.com',
            'username': 'testuser2',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23',
            'otp': '123456'
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
            'password2': 'Testp@ss!23',
            'otp': '123456'
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
            'password2': '',
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_password_mismatch(self):
        """Test creating a new user with password confirmation mismatch"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!24',
            'otp': '123456'
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
            'email': self.User.email,
            'otp': '123456'  # Assuming this is the correct OTP for the test
        }
        response = self.client.post(VERIFY_EMAIL_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.User.refresh_from_db()
        self.assertTrue(self.User.email_verified)


class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()  # Instantiate the Django REST Framework's APIClient  # noqa
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23'
        )
        self.client.force_authenticate(user=self.user)  # Force authenticate the user for subsequent requests  # noqa
