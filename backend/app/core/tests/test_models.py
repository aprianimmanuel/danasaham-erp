"""Tests for models"""

from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.email = 'test@example.com'
        self.username = 'testuser'
        self.password = 'Testp@ss!23'
        self.totp_secret = 'base32secret3232'
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password,
            totp_secret_key=self.totp_secret
        )

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        self.assertEqual(self.user.email, self.email)
        self.assertTrue(self.user.check_password(self.password))
        # Ensure the totp_secret_key gets encrypted and can be decrypted
        decrypted_totp = self.user.get_totp_secret_key()
        self.assertEqual(decrypted_totp, self.totp_secret)

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

    def test_user_id_as_primary_key(self):
        """Test that the user_id field is used as the primary key."""
        self.assertTrue(hasattr(self.user, 'user_id'))
        self.assertIsNotNone(self.user.user_id)

    def test_totp_secret_key_encryption(self):
        """Test that the TOTP secret key is encrypted."""
        user_with_totp = User.objects.create_user(
            email='totpuser@example.com',
            username='totpuser',
            password='Testp@ss!23',
            totp_secret_key='mysecretkey123'
        )
        self.assertNotEqual(user_with_totp.totp_secret_key, 'mysecretkey123')
        decrypted_key = user_with_totp.get_totp_secret_key()
        self.assertEqual(decrypted_key, 'mysecretkey123')
