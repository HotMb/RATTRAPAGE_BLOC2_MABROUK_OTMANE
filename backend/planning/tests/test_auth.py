from rest_framework.test import APITestCase
from rest_framework import status
from planning.models import User


class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)

    def test_login_returns_tokens_and_role(self):
        response = self.client.post('/api/auth/login/', {'username': 'admin1', 'password': 'pass1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['role'], 'ADMIN')
        self.assertEqual(response.data['username'], 'admin1')

    def test_login_with_wrong_password_rejected(self):
        response = self.client.post('/api/auth/login/', {'username': 'admin1', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
