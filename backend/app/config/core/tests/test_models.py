"""Tests for models."""

from __future__ import annotations

import os
import shutil
from datetime import date
from tempfile import mkdtemp

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from app.config.core.models import Document, UserProfile, dttotDoc

User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self) -> None:
        self.email = "test@example.com"
        self.username = "testuser"
        self.password = "Testp@ss!23"
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password,
        )

    def test_create_user_with_email_successful(self) -> None:
        """Test creating a user with an email is successful."""
        assert self.user.email == self.email
        assert self.user.check_password(self.password)

    def test_create_superuser(self) -> None:
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            username="adminuser",
            password="adminpass123",
        )
        assert superuser.is_staff
        assert superuser.is_superuser

    def test_new_user_email_normalized(self) -> None:
        """Test email is normalized for new users."""
        email = "testuser2@EXAMPLE.COM"
        user = User.objects.create_user(email, "sample123", password="Testp@ss!23")
        assert user.email == email.lower()

    def test_new_user_without_email_raises_error(self) -> None:
        """Test that creating a user without an email raises a ValueError."""
        with pytest.raises(ValueError):
            User.objects.create_user("", "test123", password="Testp@ss!23")

    def test_user_id_as_primary_key(self) -> None:
        """Test that the user_id field is used as the primary key."""
        assert hasattr(self.user, "user_id")
        assert self.user.user_id is not None


class UserProfileModelTests(TestCase):

    def setUp(self) -> None:
        # Create a user instance to link with UserProfile
        self.email = "test@example.com"
        self.username = "testuser"
        self.password = "Testp@ss!23"
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
            first_name="Test",
            last_name="User",
        )

    def test_user_profile_creation(self) -> None:
        """Test the user profile is created successfully."""
        assert self.user_profile.user.username == "testuser"
        assert self.user_profile.bio == "This is a test bio."
        assert self.user_profile.phone_number == "1234567890"
        assert self.user_profile.birth_date == date(1990, 1, 1)
        assert self.user_profile.first_name == "Test"
        assert self.user_profile.last_name == "User"

    def test_user_profile_str(self) -> None:
        """Test the string representation of the user profile."""
        assert str(self.user_profile) == "testuser"


class DttotDocModelTest(TestCase):

    @classmethod
    def setUp(self) -> None:
        # Setup non-modified objects used by all test methods
        self.test_user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="Testp@ss!23",
        )
        self.dttot_doc = dttotDoc.objects.create(
            user=self.test_user,
            dttot_first_name="John",
            dttot_last_name="Doe",
            dttot_type="Personal",
            dttot_domicile_address="Jalanin aja dulu",
            dttot_description_1="KENA GOCEK NIH ABANGKUUWH",
            dttot_nik_ktp="1234567890123456",
            dttot_passport_number="ABC123456",
        )

    def test_str_representation(self) -> None:
        # Test the string representation of the model
        assert str(self.dttot_doc) == "John Doe - Personal"


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "media", "test_media"))
class DocumentModelTests(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # Set up non-modified objects used by all test methods
        cls.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Testp@ss!23",
        )

    def setUp(self) -> None:
        # Create a temporary directory to serve as MEDIA_ROOT
        self.temp_media_dir = mkdtemp()

        # Apply override_settings decorator dynamically
        self.override_media_root = override_settings(MEDIA_ROOT=self.temp_media_dir)
        self.override_media_root.enable()

    def tearDown(self) -> None:
        # Disable the overridden MEDIA_ROOT setting
        self.override_media_root.disable()

        # Remove the temporary directory after the test
        shutil.rmtree(self.temp_media_dir)

    def test_document_creation(self) -> None:
        """Test the document model can be created successfully."""
        document = Document.objects.create(
            document_name="Test Document",
            description="A test document description.",
            document_type="Type1",
            created_by=self.user,
            updated_by=self.user,
        )
        assert document.document_name == "Test Document"
        assert document.description == "A test document description."
        assert document.document_type == "Type1"
        assert document.created_by == self.user
        assert document.updated_by == self.user

    def test_document_str(self) -> None:
        """Test the document string representation."""
        document = Document.objects.create(
            document_name="Test Document",
            description="A test document description.",
            document_type="PDF",
            created_by=self.user,
            updated_by=self.user,
        )
        assert str(document) == "Test Document"

    def upload_document_test_helper(self, file_name, file_content, document_type) -> None:
        document_file = SimpleUploadedFile(
            file_name,
            file_content,
            content_type="application/pdf",
        )

        document = Document.objects.create(
            document_name=file_name,
            description="A test document description.",
            document_file=document_file,
            document_type=document_type,
            created_by=self.user,
            updated_by=self.user,
        )

        # Check if document and file exist
        assert Document.objects.filter(pk=document.document_id).exists()
        assert document.document_file.name

        # Clean up the saved file
        document.document_file.delete()

    def test_document_upload_pdf(self) -> None:
        """Test uploading a PDF file."""
        self.upload_document_test_helper("test.pdf", b"PDF file content", "PDF")

    def test_document_upload_xls(self) -> None:
        """Test uploading an XLS file."""
        self.upload_document_test_helper("test.xls", b"XLS file content", "XLS")

    def test_document_upload_csv(self) -> None:
        """Test uploading a CSV file."""
        self.upload_document_test_helper("test.csv", b"CSV,Content", "CSV")

    def test_document_update(self) -> None:
        """Test updating an existing document's metadata."""
        document = Document.objects.create(
            document_name="Initial Name",
            document_type="Initial Type",
            created_by=self.user,
            updated_by=self.user,
        )
        document.document_name = "Updated Name"
        document.document_type = "Updated Type"
        document.save()
        updated_document = Document.objects.get(pk=document.pk)
        assert updated_document.document_name == "Updated Name"
        assert updated_document.document_type == "Updated Type"
