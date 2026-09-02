from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from planning.models import User, Classe


class ClasseApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)
        self.etudiant_user = User.objects.create_user(username='etu1', password='pass1234', role=User.Role.ETUDIANT)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)
        self.etudiant_client = APIClient()
        self.etudiant_client.force_authenticate(user=self.etudiant_user)

    def test_admin_can_create_classe(self):
        response = self.admin_client.post('/api/classes/', {'nom': 'BTS SIO 1', 'niveau': 'BTS1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_etudiant_can_read_but_not_create_classe(self):
        Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        list_response = self.etudiant_client.get('/api/classes/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        create_response = self.etudiant_client.post('/api/classes/', {'nom': 'X', 'niveau': 'Y'}, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_read_classes(self):
        anonymous_client = APIClient()
        response = anonymous_client.get('/api/classes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
