"""Test for the Django admin modifications."""

from __future__ import annotations

from django.contrib.auth import get_user_model  #type: ignore # noqa: PGH003
from django.test import Client, TestCase  #type: ignore # noqa: PGH003
from django.urls import reverse  #type: ignore # noqa: PGH003

from app.user.user_profile.models import UserProfile  #type: ignore # noqa: PGH003


class AdminSiteTests(TestCase):
    """Test for Django admin."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create users."""
        cls.user = get_user_model().objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Testp@ss!23",  # noqa: S106
        )

        cls.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            username="adminuser",
            password="adminpass123",  # noqa: S106
        )
        cls.user_profile = UserProfile.objects.create(
            user=cls.user,
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
            bio="Test Bio",
        )

    def setUp(self) -> None:
        """Set up client."""
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_user_list_display(self) -> None:
        """Test that custom fields are displayed in user list display."""
        response = self.client.get(reverse("admin:core_user_changelist"))
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "Test")
        self.assertContains(response, "User")

    def test_user_search_fields(self) -> None:
        """Test that search fields are properly set for user admin, including UserProfile fields."""
        # Searching by email
        search_response_email = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user.email}",
        )
        self.assertContains(search_response_email, self.user.email)

        # Searching by username
        search_response_username = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user.username}",
        )
        self.assertContains(search_response_username, self.user.username)

        # Searching by first name
        search_response_first_name = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user_profile.first_name}",
        )
        self.assertContains(search_response_first_name, self.user.email)

        # Searching by last name
        search_response_last_name = self.client.get(
            f"{reverse('admin:core_user_changelist')}?q={self.user_profile.last_name}",
        )
        self.assertContains(search_response_last_name, self.user.email)

    def test_user_filters(self) -> None:
        """Test that filters are properly set for user admin."""
        response = self.client.get(reverse("admin:core_user_changelist"))
        self.assertContains(response, "is_active")
        self.assertContains(response, "is_staff")
        self.assertContains(response, "is_superuser")

    def test_user_change_page(self) -> None:
        """Test that user change page loads properly."""
        url = reverse("admin:core_user_change", args=[self.user.user_id])
        response = self.client.get(url)
        self.assertContains(response, "Test")
        self.assertContains(response, "User")
        self.assertContains(response, "1234567890")
        self.assertContains(response, "Test Bio")

    def test_create_user_page(self) -> None:
        """Test the create user page works."""
        response = self.client.get(reverse("admin:core_user_add"))
        assert response.status_code == 200  # noqa: PLR2004, S101

