from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()
CREATE_USER_URL = reverse('user:create')
TOKEN_OBTAIN_URL = reverse('user:login')
TOTP_GENERATE_URL = reverse('user:totp_generate')
TOTP_VERIFY_URL = reverse('user:totp_verify')


class PublicUserAPITest(TestCase):
    """Test the public user API"""

    def setUp(self):
        self.client = APIClient()

    # @patch('core.models.generate_totp_secret')
    def test_create_user_success(self):
        """Test creating a new user"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23',
            'password2': 'Testp@ss!23',
        }
        response = self.client.post(
            CREATE_USER_URL,
            data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        user_exist = User.objects.filter(email=data['email']).exists()
        self.assertTrue(user_exist)

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


class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()  # Instantiate the Django REST Framework's APIClient  # noqa
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23'
        )
        self.client.force_authenticate(user=self.user)  # Force authenticate the user for subsequent requests  # noqa
