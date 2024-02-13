"""
Test for the Django admin modifications
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Test for Django admin"""

    @classmethod
    def setUpTestData(cls):
        """Create users"""
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
        )

        cls.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123',
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

    def test_user_search_fields(self):
        """Test that search fields are properly set for user admin."""
        response = self.client.get(reverse('admin:core_user_changelist'))
        self.assertContains(response, 'email')
        self.assertContains(response, 'username')

    def test_user_filters(self):
        """Test that filters are properly set for user admin."""
        response = self.client.get(reverse('admin:core_user_changelist'))
        self.assertContains(response, 'is_active')
        self.assertContains(response, 'is_staff')
        self.assertContains(response, 'is_superuser')

    def test_user_change_page(self):
        """Test that user change page loads properly."""
        response = self.client.get(reverse('admin:core_user_change', args=[self.user.id]))  # noqa
        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        response = self.client.get(reverse('admin:core_user_add'))
        self.assertEqual(response.status_code, 200)
