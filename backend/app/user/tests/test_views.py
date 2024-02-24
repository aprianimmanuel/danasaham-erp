from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_email.models import EmailDevice
from unittest.mock import patch, MagicMock
from django_otp.oath import totp
from django_otp import devices_for_user
from binascii import hexlify
import os
import time


User = get_user_model()

# Define URLs
CREATE_USER_URL = reverse('user:create')
USER_DETAIL_URL = reverse(
    'user:detail',
    kwargs={'user_id': 'mock_user_id'})
TOKEN_OBTAIN_URL = reverse('user:token_obtain')
VERIFY_TOTP_URL = reverse('user:totp_verify')


class PublicUserAPITests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_valid_payload_success(self):
        """Test creating a user with a valid payload is successful"""
        payload = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    
class PrivateUserApiTest(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
