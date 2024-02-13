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

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['testuser@EXAMPLE.COM', 'testuser@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_is_staff_status(self):
        """Test if is_staff status is not True or not set."""
        email = 'staff@example.com'
        password = 'staffpass123'
        user = get_user_model().objects.create_user(
            email=email,
            username='staffuser',
            password=password,
        )

        self.assertFalse(user.is_staff)

    def test_is_superuser_status(self):
        """Test if is_superuser status is not True or not set."""
        email = 'user@example.com'
        password = 'userpass123'
        user = get_user_model().objects.create_user(
            email=email,
            username='regularuser',
            password=password,
        )

        self.assertFalse(user.is_superuser)
