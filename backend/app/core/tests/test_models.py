"""Tests for models"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from core.models import UserProfile, dttotDoc
from cryptography.fernet import Fernet
import os


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


class UserProfileModelTests(TestCase):

    def setUp(self):
        # Create a user instance to link with UserProfile
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

        # Create a UserProfile instance
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            bio="This is a test bio.",
            phone_number="1234567890",
            birth_date=date(1990, 1, 1),
            first_name='Test',
            last_name='User'
        )

    def test_user_profile_creation(self):
        """Test the user profile is created successfully"""
        self.assertEqual(self.user_profile.user.username, 'testuser')
        self.assertEqual(self.user_profile.bio, 'This is a test bio.')
        self.assertEqual(self.user_profile.phone_number, '1234567890')
        self.assertEqual(self.user_profile.birth_date, date(1990, 1, 1))
        self.assertEqual(self.user_profile.first_name, 'Test')
        self.assertEqual(self.user_profile.last_name, 'User')

    def test_user_profile_str(self):
        """Test the string representation of the user profile"""
        self.assertEqual(str(self.user_profile), 'testuser')


class DttotDocModelTest(TestCase):

    @classmethod
    def setUp(self):
        # Setup non-modified objects used by all test methods
        self.test_user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='Testp@ss!23')
        self.dttot_doc = dttotDoc.objects.create(
            input_by=self.test_user,
            _dttot_first_name="John",
            _dttot_last_name="Doe",
            dttot_type="Personal",
            _dttot_domicile_address1="Jalanin aja dulu",
            _dttot_description_1="KENA GOCEK NIH ABANGKUUWH",
            _dttot_nik_ktp="1234567890123456",
            _dttot_passport_number="ABC123456",
            _dttot_work_number="0123456789",
            _dttot_mobile_number="0987654321",
        )

    def test_encryption(self):
        # Fetch the record directly from the database
        doc = dttotDoc.objects.get(dttot_id=self.dttot_doc.dttot_id)
        fernet = Fernet(os.getenv('FERNET_KEY').encode())

        # Check if the sensitive fields are encrypted
        self.assertNotEqual(doc._dttot_first_name, "John")
        self.assertTrue(
            fernet.decrypt(
                doc._dttot_first_name.encode()
            ).decode(), "John"
        )

    def test_decryption(self):
        # Use the model's properties to check if decryption works correctly
        self.assertEqual(self.dttot_doc.dttot_first_name, "John")
        self.assertEqual(self.dttot_doc.dttot_last_name, "Doe")
        self.assertEqual(
            self.dttot_doc.dttot_description_1, "KENA GOCEK NIH ABANGKUUWH")
        self.assertEqual(self.dttot_doc.dttot_nik_ktp, "1234567890123456")
        self.assertEqual(self.dttot_doc.dttot_passport_number, "ABC123456")
        self.assertEqual(self.dttot_doc.dttot_work_number, "0123456789")
        self.assertEqual(self.dttot_doc.dttot_mobile_number, "0987654321")

    def test_str_representation(self):
        # Test the string representation of the model
        self.assertEqual(str(self.dttot_doc), "John Doe - Personal")

    def test_update_encrypted_fields(self):
        # Test updating encrypted fields
        self.dttot_doc._dttot_first_name = "Jane"
        self.dttot_doc.save()
        self.assertEqual(self.dttot_doc.dttot_first_name, "Jane")
        # Fetch again from DB to ensure changes are persisted
        updated_doc = dttotDoc.objects.get(dttot_id=self.dttot_doc.dttot_id)
        self.assertEqual(updated_doc.dttot_first_name, "Jane")

    def test_empty_string_encryption(self):
        # Test that empty strings in encrypted fields don't raise errors
        self.dttot_doc._dttot_first_name = ""
        self.dttot_doc.save()
        self.assertEqual(self.dttot_doc.dttot_first_name, "")
        # Ensure empty value is correctly handled
        empty_val_doc = dttotDoc.objects.get(dttot_id=self.dttot_doc.dttot_id)
        self.assertEqual(empty_val_doc.dttot_first_name, "")

    def test_user_deletion_cascade(self):
        # Test dttotDoc instances are deleted when the related User is deleted
        self.test_user.delete()
        dttot_doc_instance = dttotDoc.objects.get(
            dttot_id=self.dttot_doc.dttot_id)
        self.assertIsNone(dttot_doc_instance.input_by)
