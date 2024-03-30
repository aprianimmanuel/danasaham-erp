from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import UserProfile
from unittest.mock import patch
from django.core import mail

User = get_user_model()


class PublicUserAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse('rest_register')

    def test_user_registration_valid(self):
        """
        Test registering a user with valid data is successful.
        """
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Testpass!123',
            'password2': 'Testpass!123',
        }
        response = self.client.post(self.registration_url, user_data)
        try:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        except AssertionError as e:
            print("Failed to register user. Response:", response.content)
            raise e

    def test_user_registration_password_mismatch(self):
        """
        Test registering a user with passwords that do not match fails.
        """
        user_data = {
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password1': 'Testpass!123',
            'password2': 'Testpass!124',
        }
        response = self.client.post(self.registration_url, user_data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_short_password(self):
        """
        Test registering a user with a short password fails.
        """
        user_data = {
            'username': 'shortpassword',
            'email': 'shortpass@example.com',
            'password1': 'short',
            'password2': 'short',
        }
        response = self.client.post(self.registration_url, user_data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_no_email(self):
        """
        Test registering a user without an email fails.
        """
        user_data = {
            'username': 'noemail',
            'password1': 'Testpass!123',
            'password2': 'Testpass!123',
        }
        response = self.client.post(self.registration_url, user_data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_existing_username(self):
        """
        Test registering a user with an existing username fails.
        """
        user_data_1 = {
            'username': 'uniqueuser',
            'email': 'uniqueuser1@example.com',
            'password1': 'Testpass!123',
            'password2': 'Testpass!123',
        }
        user_data_2 = {
            'username': 'uniqueuser',
            'email': 'uniqueuser2@example.com',
            'password1': 'Testpass!123',
            'password2': 'Testpass!123',
        }
        self.client.post(self.registration_url, user_data_1)
        response = self.client.post(self.registration_url, user_data_2)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_existing_email(self):
        """
        Test registering a user with an existing email fails.
        """
        user_data_1 = {
            'username': 'useremail1',
            'email': 'sameemail@example.com',
            'password1': 'Testpass!23',
            'password2': 'Testpass!23',
        }
        user_data_2 = {
            'username': 'useremail2',
            'email': 'sameemail@example.com',
            'password1': 'Testpass!23',
            'password2': 'Testpass!23',
        }
        self.client.post(self.registration_url, user_data_1)
        response = self.client.post(self.registration_url, user_data_2)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)


class PrivateUserAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testpass!23'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            first_name='TestName',
            last_name='TestSurname')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_profile_retrieve(self):
        profile_url = reverse('rest_details')
        response = self.client.get(profile_url)

        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(
            response.data.get(
                'first_name'
            ), self.user_profile.first_name)

    def test_user_profile_update(self):
        profile_url = reverse('rest_details')
        update_data = {'first_name': 'NewName'}
        response = self.client.patch(profile_url, update_data)
        self.user_profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user_profile.first_name, 'NewName')

    def test_user_change_password(self):
        change_password_url = reverse('rest_password_change')
        password_data = {
            'old_password': 'Testpass!23',
            'new_password1': 'NewTestpass!123',
            'new_password2': 'NewTestpass!123',
        }
        response = self.client.post(change_password_url, password_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('dj_rest_auth.registration.views.ConfirmEmailView.get_object')
    def test_user_email_verification(self, mock_get_object):
        mock_confirm = mock_get_object.return_value
        mock_confirm.confirm.return_value = True
        email_verification_url = reverse('rest_verify_email')
        response = self.client.post(
            email_verification_url,
            {
                'key': 'dummy-key'
                }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_password_reset(self):
        password_reset_url = reverse('rest_password_reset')
        reset_data = {'email': self.user.email}
        response = self.client.post(password_reset_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirmation(self):
        # Request a password reset (this should trigger an email to be sent)
        self.client.post(
            reverse('rest_password_reset'), {'email': self.user.email})

        # Ensure an email has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Extract the password reset token and uidb64 from the email
        email_body = mail.outbox[0].body

        import re
        reset_link_pattern = re.compile(
            r'http://testserver(/api/user/password/reset/confirm/(?P<uidb64>[0-9a-f-]+)/(?P<token>[0-9A-Za-z-]+)/)')  # noqa
        match = reset_link_pattern.search(email_body)

        print("Email Body:", email_body)  # Debugging print

        if not match:
            self.fail("Reset URL not found in email body.")

        uidb64, token = match.group('uidb64'), match.group('token')

        # Prepare data for password reset confirmation
        post_data = {
            'uid': uidb64,
            'token': token,
            'new_password1': 'NewPassword123',
            'new_password2': 'NewPassword123',
        }
        # Construct URL for password reset confirmation
        confirm_url = f"/api/user/password/reset/confirm/{uidb64}/{token}/"

        # Make the POST request
        response = self.client.post(confirm_url, post_data)

        # Assert response status
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            f"Response content: {response.content}")

        # Verify the user's password was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))

    def test_unauthorized_access(self):
        self.client.logout()
        profile_url = reverse('rest_details')
        response = self.client.get(profile_url)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
