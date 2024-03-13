"""
Test for the Django admin modifications
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import UserProfile, dttotDoc
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class AdminSiteTests(TestCase):
    """Test for Django admin"""

    @classmethod
    def setUpTestData(cls):
        """Create users"""
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23',
        )

        cls.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123',
        )
        cls.user_profile = UserProfile.objects.create(
            user=cls.user,
            first_name='Test',
            last_name='User',
            phone_number='1234567890',
            bio='Test Bio'
        )

    def setUp(self):
        """Set up client"""
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_user_list_display(self):
        """Test that custom fields are displayed in user list display."""
        response = self.client.get(reverse('admin:core_user_changelist'))
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.username)
        self.assertContains(response, 'Test')
        self.assertContains(response, 'User')

    def test_user_search_fields(self):
        """Test that search fields are properly set for user admin,
        including UserProfile fields.
        """
        # Searching by email
        search_response_email = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user.email}")
        self.assertContains(search_response_email, self.user.email)

        # Searching by username
        search_response_username = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user.username}")
        self.assertContains(search_response_username, self.user.username)

        # Searching by first name
        search_response_first_name = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user_profile.first_name}")  # noqa
        self.assertContains(search_response_first_name, self.user.email)

        # Searching by last name
        search_response_last_name = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user_profile.last_name}")  # noqa
        self.assertContains(search_response_last_name, self.user.email)

    def test_user_filters(self):
        """Test that filters are properly set for user admin."""
        response = self.client.get(reverse('admin:core_user_changelist'))
        self.assertContains(response, 'is_active')
        self.assertContains(response, 'is_staff')
        self.assertContains(response, 'is_superuser')

    def test_user_change_page(self):
        """Test that user change page loads properly."""
        url = reverse('admin:core_user_change', args=[self.user.user_id])
        response = self.client.get(url)
        self.assertContains(response, 'Test')
        self.assertContains(response, 'User')
        self.assertContains(response, '1234567890')
        self.assertContains(response, 'Test Bio')

    def test_create_user_page(self):
        """Test the create user page works."""
        response = self.client.get(reverse('admin:core_user_add'))
        self.assertEqual(response.status_code, 200)


class DttotDocAdminTest(TestCase):

    def setUp(self):
        """Set up for the tests"""
        # Create a superuser and log them in
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123',
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

        # Create a normal user
        self.normal_user = get_user_model().objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23',
            email_verified=True
        )
        self.api_client = APIClient()
        self.token, _ = Token.objects.get_or_create(
            user=self.normal_user)
        self.api_client.force_authenticate(
            user=self.normal_user,
            token=self.token.key
        )

        # Create a DttotDoc instance
        self.dttot_doc = dttotDoc.objects.create(
            input_by=self.normal_user,
            dttot_type="Personal",
            _dttot_first_name="John",
            _dttot_last_name="Doe"
        )

    def test_list_display(self):
        """Test that dttotDoc list display includes specific fields"""
        url = reverse('admin:core_dttotdoc_changelist')
        response = self.client.get(url)
        self.assertContains(response, self.dttot_doc.dttot_type)
        self.assertContains(response, self.normal_user.username)
        self.assertContains(response, self.dttot_doc.updated_at.date())

    def test_search_fields(self):
        """Test the search functionality for dttotDoc in the Django admin."""
        url = reverse('admin:core_dttotdoc_changelist') + '?q=John'
        response = self.client.get(url)
        self.assertContains(response, "John")
        url_doe = reverse('admin:core_dttotdoc_changelist') + '?q=Doe'
        response_doe = self.client.get(url_doe)
        self.assertContains(response_doe, "Doe")

    def test_filters(self):
        """Test the filters for dttotDoc in the Django admin"""
        url = reverse(
            'admin:core_dttotdoc_changelist'
        ) + f'?dttot_type={self.dttot_doc.dttot_type}'
        response = self.client.get(url)
        self.assertContains(response, self.dttot_doc.dttot_type)

    def test_change_page(self):
        """Test that the dttotDoc change page works"""
        url = reverse(
            'admin:core_dttotdoc_change',
            args=[self.dttot_doc.document_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_page(self):
        """Test the dttotDoc create page"""
        url = reverse('admin:core_dttotdoc_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
