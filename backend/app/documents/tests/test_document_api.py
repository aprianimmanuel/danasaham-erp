import shutil
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import Document
from django.conf import settings


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
