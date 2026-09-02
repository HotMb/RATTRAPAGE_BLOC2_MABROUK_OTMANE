from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from planning.models import User, Classe, Etudiant


class IntervenantEtudiantApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)

        self.etudiant_user = User.objects.create_user(username='etu1', password='pass1234', role=User.Role.ETUDIANT)
        self.etudiant_client = APIClient()
        self.etudiant_client.force_authenticate(user=self.etudiant_user)

        self.classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')

    def test_admin_creates_intervenant_with_linked_user_in_one_call(self):
        payload = {
            'nom': 'Dupont', 'prenom': 'Jean', 'email': 'j.dupont@efficom.fr',
            'username': 'jdupont', 'password': 'motdepasse123',
        }
        response = self.admin_client.post('/api/intervenants/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(username='jdupont')
        self.assertEqual(created_user.role, User.Role.INTERVENANT)
        self.assertTrue(created_user.check_password('motdepasse123'))

    def test_admin_creates_etudiant_with_classe_and_linked_user(self):
        payload = {
            'nom': 'Martin', 'prenom': 'Alice', 'email': 'a.martin@efficom.fr',
            'classe': self.classe.id, 'username': 'amartin', 'password': 'motdepasse123',
        }
        response = self.admin_client.post('/api/etudiants/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        etudiant = Etudiant.objects.get(user__username='amartin')
        self.assertEqual(etudiant.classe, self.classe)

    def test_etudiant_cannot_access_intervenants_endpoint(self):
        response = self.etudiant_client.get('/api/intervenants/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
