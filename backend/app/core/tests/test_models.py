"""Tests for models"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django_otp.oath import totp
import time

User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.email = 'test@example.com'
        self.username = 'testuser'
        self.password = 'Testp@ss!23'
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password
        )

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        self.assertEqual(self.user.email, self.email)
        self.assertTrue(self.user.check_password(self.password))

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123',
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        email = 'testuser2@EXAMPLE.COM'
        user = User.objects.create_user(email, 'sample123',
                                        password='Testp@ss!23')
        self.assertEqual(user.email, email.lower())

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user('', 'test123', password='Testp@ss!23')

    def test_generate_totp_secret(self):
        """Test generating a TOTP secret key for the user."""
        self.user.generate_totp_secret()
        self.assertIsNotNone(self.user.totp_secret_key)
        self.assertEqual(len(self.user.totp_secret_key), 40)  # 20 bytes hex encoded


