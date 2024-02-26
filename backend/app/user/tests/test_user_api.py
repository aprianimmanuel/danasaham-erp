from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from django_otp.plugins.otp_email.models import EmailDevice  # noqa
from django_otp import devices_for_user  # noqa
from django_otp.oath import totp
import uuid


User = get_user_model()
CREATE_USER_URL = reverse('user:create')
TOKEN_OBTAIN_URL = reverse('user:login')
MANAGE_USER_URL = reverse('user:me')
VERIFY_EMAIL_URL = reverse('user:verify_email')

class MockQuerySet:
    def __init__(self, *args):
        self._items = list(args)

    def filter(self, **kwargs):
        filtered_items = [
            item for item in self._items if all(getattr(item, k) == v for k, v in kwargs.items())   # noqa
        ]
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
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23',
        }

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
        }

        # Set up MagicMock to simulate QuerySet behavior
        mock_device = MagicMock(spec=EmailDevice)
        mock_device.verify_token.return_value = True
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = [mock_device]  # Simulate filter returning a list

        # Use MockQuerySet to simulate queryset behavior
        mocked_devices_for_user.return_value = MockQuerySet(mock_device)

        response = self.client.post(CREATE_USER_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_password_too_short_error(self):
        """Test creating a user with a password that is too short"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'pw',
            'password2': 'pw',
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
            'password2': 'Testp@ss!23',
        }
        create_user_response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)  # noqa

        duplicate_email_data = {
            'email': 'test@example.com',
            'username': 'testuser2',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23',
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
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def create_user_and_device(self):
        # Create a user
        response = self.client.post(CREATE_USER_URL, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Retrieve the created user
        user = User.objects.get(email=self.user_data['email'])
        # Create an EmailDevice for OTP
        device = EmailDevice.objects.create(user=user, confirmed=False)
        return user, device

    def test_email_verification_success(self):
        user, device = self.create_user_and_device()
        # Generate a valid OTP token
        valid_token = totp(device.bin_key, step=30)
        verification_data = {
            'email': user.email,
            'token': valid_token,
        }
        response = self.client.post(VERIFY_EMAIL_URL, verification_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.email_verified)

    def test_verify_email_user_not_found(self):
        user, device = self.create_user_and_device()
        # Generate a valid OTP token
        valid_token = totp(device.bin_key, step=30)
        data = {
            'email': 'nonexistence@example.com',
            'token': '123456'
        }
        response = self.client.post(VERIFY_EMAIL_URL, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23',
            password2='Testp@ss!23'
        )
        self.client.force_authenticate(user=self.user)  # Force authenticate the user for subsequent requests  # noqa
