from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app.config.core.models import UserProfile

User = get_user_model()


class PublicUserAPITests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.registration_url = reverse("rest_register")

    def test_user_registration_valid(self) -> None:
        """Test registering a user with valid data is successful."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "Testpass!123",
            "password2": "Testpass!123",
        }
        response = self.client.post(self.registration_url, user_data)
        try:
            assert response.status_code == status.HTTP_201_CREATED  #noqa: S101
        except AssertionError as e:
            print("Failed to register user. Response:", response.content)
            raise

    def test_user_registration_password_mismatch(self) -> None:
        """Test registering a user with passwords that do not match fails."""
        user_data = {
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password1": "Testpass!123",
            "password2": "Testpass!124",
        }
        response = self.client.post(self.registration_url, user_data)
        assert response.status_code != status.HTTP_201_CREATED  # noqa: S101

    def test_user_registration_short_password(self) -> None:
        """Test registering a user with a short password fails."""
        user_data = {
            "username": "shortpassword",
            "email": "shortpass@example.com",
            "password1": "short",
            "password2": "short",
        }
        response = self.client.post(self.registration_url, user_data)
        assert response.status_code != status.HTTP_201_CREATED  #noqa: S101

    def test_user_registration_no_email(self) -> None:
        """Test registering a user without an email fails."""
        user_data = {
            "username": "noemail",
            "password1": "Testpass!123",
            "password2": "Testpass!123",
        }
        response = self.client.post(self.registration_url, user_data)
        assert response.status_code != status.HTTP_201_CREATED  # noqa: S101

    def test_user_registration_existing_username(self) -> None:
        """Test registering a user with an existing username fails."""
        user_data_1 = {
            "username": "uniqueuser",
            "email": "uniqueuser1@example.com",
            "password1": "Testpass!123",
            "password2": "Testpass!123",
        }
        user_data_2 = {
            "username": "uniqueuser",
            "email": "uniqueuser2@example.com",
            "password1": "Testpass!123",
            "password2": "Testpass!123",
        }
        self.client.post(self.registration_url, user_data_1)
        response = self.client.post(self.registration_url, user_data_2)
        assert response.status_code != status.HTTP_201_CREATED  #noqa: S101

    def test_user_registration_existing_email(self) -> None:
        """Test registering a user with an existing email fails."""
        user_data_1 = {
            "username": "useremail1",
            "email": "sameemail@example.com",
            "password1": "Testpass!23",
            "password2": "Testpass!23",
        }
        user_data_2 = {
            "username": "useremail2",
            "email": "sameemail@example.com",
            "password1": "Testpass!23",
            "password2": "Testpass!23",
        }
        self.client.post(self.registration_url, user_data_1)
        response = self.client.post(self.registration_url, user_data_2)
        assert response.status_code != status.HTTP_201_CREATED  #noqa: S101


class PrivateUserAPITests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Testpass!23",
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            first_name="TestName",
            last_name="TestSurname",
        )

        # Obtain JWT token
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"email": "test@example.com", "password": "Testpass!23"},
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        self.verify_url = reverse("token_verify")

    def test_token_verify(self) -> None:
        # Verify token
        verify_response = self.client.post(self.verify_url, {"token": self.token})
        assert verify_response.status_code == status.HTTP_200_OK  #noqa: S101

    def test_user_profile_retrieve(self) -> None:
        profile_url = reverse("rest_details")
        response = self.client.get(profile_url)
        assert response.status_code == status.HTTP_200_OK  #noqa: S101
        assert response.data["email"] == self.user.email  #noqa: S101
        assert response.data["username"] == self.user.username  #noqa: S101
        assert response.data["first_name"] == self.user_profile.first_name  #noqa: S101

    def test_user_profile_update(self) -> None:
        profile_url = reverse("rest_details")
        update_data = {"first_name": "NewName"}
        response = self.client.patch(profile_url, update_data)
        self.user_profile.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK  #noqa: S101
        assert self.user_profile.first_name == "NewName"  #noqa: S101

    def test_user_change_password(self) -> None:
        change_password_url = reverse("rest_password_change")
        password_data = {
            "old_password": "Testpass!23",
            "new_password1": "NewTestpass!123",
            "new_password2": "NewTestpass!123",
        }
        response = self.client.post(change_password_url, password_data)
        self.user.refresh_from_db()
        assert self.user.check_password("NewTestpass!123")  #noqa: S101
        assert response.status_code == status.HTTP_200_OK  #noqa: S101

    @patch("dj_rest_auth.registration.views.ConfirmEmailView.get_object")
    def test_user_email_verification(self, mock_get_object) -> None:
        mock_confirm = mock_get_object.return_value
        mock_confirm.confirm.return_value = True
        email_verification_url = reverse("rest_verify_email")
        response = self.client.post(email_verification_url, {"key": "dummy-key"})
        assert response.status_code == status.HTTP_200_OK  #noqa: S101

    def test_user_password_reset(self) -> None:
        password_reset_url = reverse("rest_password_reset")
        reset_data = {"email": self.user.email}
        response = self.client.post(password_reset_url, reset_data)
        assert response.status_code == status.HTTP_200_OK  #noqa: S101

    def test_password_reset_confirmation(self) -> None:
        # Request a password reset
        self.client.post(reverse("rest_password_reset"), {"email": self.user.email})

        # Check the email box
        assert len(mail.outbox) == 1  #noqa: S101

        # Extract the password reset token and uidb64 from the email
        email_body = mail.outbox[0].body
        import re

        reset_link_pattern = re.compile(
            r"http://testserver/api/user/password/reset/confirm/(?P<uidb64>[0-9a-f-]+)/(?P<token>[0-9A-Za-z-]+)/",
        )
        match = reset_link_pattern.search(email_body)

        if not match:
            self.fail("Reset URL not found in email body.")

        uidb64 = match.group("uidb64")
        token = match.group("token")
        post_data = {
            "uid": uidb64,
            "token": token,
            "new_password1": "NewPassword123",
            "new_password2": "NewPassword123",
        }
        confirm_url = f"/api/user/password/reset/confirm/{uidb64}/{token}/"
        response = self.client.post(confirm_url, post_data)
        assert response.status_code == status.HTTP_200_OK  #noqa: S101

        # Verify password was updated
        self.user.refresh_from_db()
        assert self.user.check_password("NewPassword123")  #noqa: S101

    def test_unauthorized_access(self) -> None:
        self.client.logout()
        profile_url = reverse("rest_details")
        response = self.client.get(profile_url)
        assert response.status_code != status.HTTP_200_OK  #noqa: S101
