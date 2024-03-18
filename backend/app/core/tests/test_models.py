"""Tests for models"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from datetime import date
from core.models import UserProfile, dttotDoc, Document
from cryptography.fernet import Fernet
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from tempfile import TemporaryDirectory


User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.email = 'test@example.com'
        self.username = 'testuser'
        self.password = 'Testp@ss!23'
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password,
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

    def test_user_id_as_primary_key(self):
        """Test that the user_id field is used as the primary key."""
        self.assertTrue(hasattr(self.user, 'user_id'))
        self.assertIsNotNone(self.user.user_id)


class UserProfileModelTests(TestCase):

    def setUp(self):
        # Create a user instance to link with UserProfile
        self.email = 'test@example.com'
        self.username = 'testuser'
        self.password = 'Testp@ss!23'
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password,
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


@override_settings(
    MEDIA_ROOT=os.path.join(
        settings.BASE_DIR, 'media', 'test_media'))
class DocumentModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23'
        )

    def setUp(self):
        # Ensure the base directory for temporary media files exists
        documents_media_base_dir = os.path.join(
            settings.BASE_DIR, 'media', 'test_media')
        os.makedirs(documents_media_base_dir, exist_ok=True)

        # Now create the TemporaryDirectory within the ensured base directory
        self.media_root = TemporaryDirectory(dir=documents_media_base_dir)
        self.original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.media_root.name

    def test_document_creation(self):
        """Test the document model can be created successfully."""
        document = Document.objects.create(
            document_name='Test Document',
            description='A test document description.',
            document_type='Type1',
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(document.document_name, 'Test Document')
        self.assertEqual(document.description, 'A test document description.')
        self.assertEqual(document.document_type, 'Type1')
        self.assertEqual(document.created_by, self.user)
        self.assertEqual(document.updated_by, self.user)

    def test_document_str(self):
        """Test the document string representation."""
        document = Document.objects.create(
            document_name='Test Document',
            description='A test document description.',
            document_type='Type1',
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(str(document), 'Test Document')

    def upload_document_test_helper(self, filename, content, document_type):
        """Helper function to test document uploads."""
        upload_file = SimpleUploadedFile(
            name=filename,
            content=content,
            content_type='application/octet-stream')
        document = Document.objects.create(
            document_name=filename,
            document_file=upload_file,
            document_type=document_type,
            created_by=self.user,
            updated_by=self.user
        )
        self.assertTrue(os.path.exists(document.document_file.path))
        # Clean up file after test
        document.document_file.delete()

    def test_document_upload_pdf(self):
        """Test uploading a PDF file."""
        self.upload_document_test_helper(
            'test.pdf', b'PDF file content', 'PDF')

    def test_document_upload_xls(self):
        """Test uploading an XLS file."""
        self.upload_document_test_helper(
            'test.xls', b'XLS file content', 'XLS')

    def test_document_upload_csv(self):
        """Test uploading a CSV file."""
        self.upload_document_test_helper(
            'test.csv', b'CSV,Content', 'CSV')

    def test_document_update(self):
        """Test updating an existing document's metadata."""
        document = Document.objects.create(
            document_name='Initial Name',
            document_type='Initial Type',
            created_by=self.user,
            updated_by=self.user
        )
        document.document_name = 'Updated Name'
        document.document_type = 'Updated Type'
        document.save()
        updated_document = Document.objects.get(pk=document.pk)
        self.assertEqual(updated_document.document_name, 'Updated Name')
        self.assertEqual(updated_document.document_type, 'Updated Type')

    def tearDown(self):
        # Clean up the temporary directory and
        # restore the original MEDIA_ROOT after the test
        self.media_root.cleanup()
        settings.MEDIA_ROOT = self.original_media_root
