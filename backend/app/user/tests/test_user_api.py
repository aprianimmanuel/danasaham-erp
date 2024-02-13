"""
Tests for the user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils.crypto import get_random_string

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

User = get_user_model()


def create_user(**params):
    """Helper function to create a user"""
    return User.objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """Test the public user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a new user"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testp@ss!23'
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=data['email'])
        self.assertTrue(user.check_password(data['password']))
        self.assertNotIn('password', response.data)

    def test_password_too_short_error(self):
        """Test creating a user with a password that is too short"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'pw'
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_create_user_invalid_data(self):
        """Test creating a new user with invalid data"""
        invalid_data = [
            {'email': '', 'username': 'testuser', 'password': 'testpass123'},  # Empty email  # noqa
            {'email': 'invalidemail', 'username': 'testuser', 'password': 'testpass123'},  # Invalid email format  # noqa
            {'email': 'test@example.com', 'username': '', 'password': 'testpass123'},  # Empty username  # noqa
            {'email': 'test@example.com', 'username': 'testuser', 'password': ''},  # Empty password  # noqa
            {'email': 'test@example.com', 'username': 'test_user#1', 'password': 'testpass123'},  # Invalid username with special characters  # noqa
        ]

        for data in invalid_data:
            response = self.client.post(CREATE_USER_URL, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        for key in data:
            if key in response.data:
                self.assertIn(key, response.data)

            user_exists = User.objects.filter(email=data.get('email', '')).exists()  # noqa
            self.assertFalse(user_exists, f"User should not be created with data: {data}")  # noqa

    def test_create_user_duplicate_username(self):
        """Test creating a new user with a duplicate username"""
        data = {
            'email': 'test1@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        create_user(**data)  # Create a user with the same username first
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_duplicate_email(self):
        """Test creating a new user with a duplicate email address"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser1',
            'password': 'testpass123'
        }
        create_user(**data)  # Create a user with the same email address first
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_missing_required_fields(self):
        """Test creating a new user with missing required fields"""
        data = {'email': '', 'username': '', 'password': ''}
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_unique_email_constraint(self):
        """Test creating a new user with a non-unique email address"""
        data1 = {'email': 'test@example.com', 'username': 'testuser1', 'password': 'testpass123'}  # noqa
        create_user(**data1)  # Create a user with the same email address first

        data2 = {'email': 'test@example.com', 'username': 'testuser2', 'password': 'testpass123'}  # noqa
        response = self.client.post(CREATE_USER_URL, data2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Test generating token for valid credentials."""
        # Generate unique email and username
        email = f'test{get_random_string()}@example.com'
        username = f'testuser{get_random_string()}'
        password = get_random_string()

        data = {
            'email': email,
            'username': username,
            'password': password,
        }

        # Create a new user with unique credentials
        create_user(**data)

        payload = {
            'username': username,
            'password': password,
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password"""
        create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23'
        )
        payload = {'email': 'test@example.com', 'password': ''}
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_missing_email(self):
        """Test posting a request with missing email"""
        payload = {'password': 'Testp@ss!23'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_missing_password(self):
        """Test posting a request with missing password"""
        payload = {'email': 'test@example.com'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_invalid_credentials(self):
        """Test posting a request with invalid email and password"""
        payload = {'email': 'invalid@example.com', 'password': 'invalidpassword'}  # noqa
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_inactive_user(self):
        """Test posting a request with inactive user"""
        create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23',
            is_active=False
        )
        payload = {'email': 'test@example.com', 'password': 'Testp@ss!23'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)
