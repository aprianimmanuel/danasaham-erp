"""Tests for models"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            username='testuser',
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_superuser(self):
        """Test creating a superuser"""
        email = 'admin@example.com'
        password = 'adminpass123'
        superuser = get_user_model().objects.create_superuser(
            email=email,
            username='adminuser',
            password=password,
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
