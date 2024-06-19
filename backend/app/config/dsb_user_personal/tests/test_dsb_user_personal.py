from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.config.core.models import dsb_user_personal, User
from rest_framework.authtoken.models import Token
import uuid


class DsbUserPersonalTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='t3Stp@ssw0rd')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.dsb_user_personal = dsb_user_personal.objects.create(
            user_id=self.user.user_id,
            personal_nik='1234567890123456',
            user_name='Test User'
        )

    def test_list_dsb_user_personal(self):
        url = reverse('dsb_user_personal:dsb_user_personal-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_dsb_user_personal(self):
        url = reverse('dsb_user_personal:dsb_user_personal-list')
        data = {
            'user_id': self.user.user_id,
            'personal_nik': '2345678901234567',
            'user_name': 'New Test User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(dsb_user_personal.objects.count(), 2)
        self.assertEqual(dsb_user_personal.objects.get(personal_nik='2345678901234567').user_name, 'New Test User')

    def test_retrieve_dsb_user_personal(self):
        url = reverse('dsb_user_personal:dsb_user_personal-details', args=[self.dsb_user_personal.user_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['personal_nik'], self.dsb_user_personal.personal_nik)

    def test_update_dsb_user_personal(self):
        url = reverse('dsb_user_personal:dsb_user_personal-details', args=[self.dsb_user_personal.user_id])
        data = {
            'user_id': self.user.user_id,
            'personal_nik': '1234567890123456',
            'user_name': 'Updated Test User'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dsb_user_personal.refresh_from_db()
        self.assertEqual(self.dsb_user_personal.user_name, 'Updated Test User')

    def test_partial_update_dsb_user_personal(self):
        url = reverse('dsb_user_personal:dsb_user_personal-details', args=[self.dsb_user_personal.user_id])
        data = {
            'user_name': 'Partially Updated Test User'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dsb_user_personal.refresh_from_db()
        self.assertEqual(self.dsb_user_personal.user_name, 'Partially Updated Test User')

    def test_delete_dsb_user_personal(self):
        url = reverse('dsb_user_personal:dsb_user_personal-details', args=[self.dsb_user_personal.user_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(dsb_user_personal.objects.count(), 0)
