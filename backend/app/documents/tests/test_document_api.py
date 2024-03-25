import shutil
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from core.models import Document, dttotDoc
from django.conf import settings
import os
from tempfile import TemporaryDirectory


def document_list_url():
    return reverse('document-list')


def document_detail_url(document_pk):
    return reverse('document-detail', args=[document_pk])


class DocumentAPITests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com', 'password123')

    def tearDown(self):
        # Cleanup the MEDIA_ROOT directory after each test
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_create_document(self):
        """Test creating a document."""
        self.client.force_authenticate(user=self.user)
        payload = {
            'document_name': 'Test Name',
            'document_type': 'PDF',
            'description': 'Test Description',
            'document_file': SimpleUploadedFile(
                'document.pdf',
                b'Test content',
                content_type='application/pdf')
        }
        res = self.client.post(
            document_list_url(),
            payload,
            format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        document = Document.objects.get(pk=res.data['document_id'])
        for key in payload.keys():
            if key != 'document_file':
                self.assertEqual(payload[key], getattr(document, key))
        self.assertTrue(document.document_file)

    def test_retrieve_documents_list(self):
        """Test retrieving a list of documents."""
        Document.objects.create(
            document_name='Test1',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)
        Document.objects.create(
            document_name='Test2',
            document_type='DOCX',
            created_by=self.user,
            updated_by=self.user)

        res = self.client.get(document_list_url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_document_detail(self):
        """Test retrieving a document's detail."""
        document = Document.objects.create(
            document_name='Test',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)

        url = document_detail_url(document.pk)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['document_name'], document.document_name)

    def test_update_document(self):
        """Test updating a document."""
        document = Document.objects.create(
            document_name='Initial Name',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)

        payload = {'document_name': 'Updated Name', 'document_type': 'DOCX'}
        url = document_detail_url(document.pk)
        self.client.force_authenticate(user=self.user)
        res = self.client.patch(url, payload)

        document.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(document.document_name, payload['document_name'])
        self.assertEqual(document.document_type, payload['document_type'])

    def test_delete_document(self):
        """Test deleting a document."""
        document = Document.objects.create(
            document_name='Test',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)

        url = document_detail_url(document.pk)
        self.client.force_authenticate(user=self.user)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Document.objects.filter(
                pk=document.pk).exists())


class DTTOTDocumentUploadTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com', 'password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Create a TemporaryDirectory for MEDIA_ROOT
        self.temp_media_dir = TemporaryDirectory()
        self.addCleanup(self.temp_media_dir.cleanup)  # Ensure cleanup
        # Update MEDIA_ROOT to use the temporary directory
        self.original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.temp_media_dir.name

    def tearDown(self):
        # Reset MEDIA_ROOT to its original value
        settings.MEDIA_ROOT = self.original_media_root
        super().tearDown()

    def test_upload_dttot_document_and_process(self):
        """Test uploading a 'DTTOT Document', processing it, and saving to dttotDoc models."""  # noqa
        document_path = os.path.join(self.temp_media_dir.name, 'document.csv')
        # Create a temporary CSV file in the temporary directory
        with open(document_path, 'w') as temp_file:
            temp_file.write("Sample data")

        # Step 1: Upload the document
        upload_url = document_list_url()
        with open(document_path, 'rb') as doc_file:
            upload_payload = {
                'document_name': 'DTTOT Upload Test',
                'document_type': 'DTTOT Document',
                'document_file': doc_file
            }
            response = self.client.post(
                upload_url, upload_payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        document_id = response.data['document_id']
        self.assertTrue(Document.objects.filter(pk=document_id).exists())

        # Step 2: Trigger processing of the uploaded document
        process_url = reverse('dttot-process', args=[document_id])
        process_response = self.client.post(process_url)
        self.assertEqual(process_response.status_code, status.HTTP_200_OK)

        # Step 3:
        # Verify the document was processed and saved into dttotDoc models
        self.assertTrue(dttotDoc.objects.exists())

        # Cleanup: Optionally, delete the uploaded document if not needed
        delete_url = document_detail_url(document_id)
        delete_response = self.client.delete(delete_url)
        self.assertEqual(
            delete_response.status_code, status.HTTP_204_NO_CONTENT)
