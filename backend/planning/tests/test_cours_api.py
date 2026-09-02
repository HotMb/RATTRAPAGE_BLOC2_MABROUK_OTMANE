from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils.timezone import make_aware
from datetime import datetime

from planning.models import User, Classe, Salle, Intervenant, Etudiant, Cours


def dt(y, m, d, h, mi=0):
    return make_aware(datetime(y, m, d, h, mi)).isoformat()


class CoursApiTests(APITestCase):
    def setUp(self):
        self.classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        self.classe2 = Classe.objects.create(nom='BTS SIO 2', niveau='BTS2')
        self.salle = Salle.objects.create(nom_ou_numero='A101', capacite=30, type='TD')
        self.salle2 = Salle.objects.create(nom_ou_numero='A102', capacite=30, type='TD')

        self.admin = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)

        interv_user = User.objects.create_user(username='interv1', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant = Intervenant.objects.create(user=interv_user, nom='Dupont', prenom='Jean', email='j@efficom.fr')
        interv_user2 = User.objects.create_user(username='interv2', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant2 = Intervenant.objects.create(user=interv_user2, nom='Martin', prenom='Alice', email='a@efficom.fr')

        etu_user = User.objects.create_user(username='etu1', password='pass1234', role=User.Role.ETUDIANT)
        self.etudiant = Etudiant.objects.create(user=etu_user, nom='Petit', prenom='Sam', email='s@efficom.fr', classe=self.classe)

        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)
        self.intervenant_client = APIClient()
        self.intervenant_client.force_authenticate(user=interv_user)
        self.etudiant_client = APIClient()
        self.etudiant_client.force_authenticate(user=etu_user)

        self.existing = Cours.objects.create(
            intitule='Maths', classe=self.classe, salle=self.salle, intervenant=self.intervenant,
            debut=make_aware(datetime(2026, 9, 10, 9)), fin=make_aware(datetime(2026, 9, 10, 10)),
        )

    def _payload(self, **overrides):
        payload = {
            'intitule': 'Anglais', 'classe': self.classe2.id, 'salle': self.salle2.id,
            'intervenant': self.intervenant2.id,
            'debut': dt(2026, 9, 10, 14), 'fin': dt(2026, 9, 10, 15),
        }
        payload.update(overrides)
        return payload

    def test_create_valid_cours(self):
        response = self.admin_client.post('/api/cours/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fin_before_or_equal_debut_rejected(self):
        response = self.admin_client.post(
            '/api/cours/', self._payload(fin=dt(2026, 9, 10, 14)), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_salle_conflict_returns_409(self):
        response = self.admin_client.post(
            '/api/cours/',
            self._payload(salle=self.salle.id, debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_intervenant_conflict_returns_409(self):
        response = self.admin_client.post(
            '/api/cours/',
            self._payload(intervenant=self.intervenant.id, debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_consecutive_cours_accepted(self):
        response = self.admin_client.post(
            '/api/cours/',
            self._payload(salle=self.salle.id, classe=self.classe.id, intervenant=self.intervenant.id,
                           debut=dt(2026, 9, 10, 10), fin=dt(2026, 9, 10, 11)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_updating_cours_excludes_itself_from_conflict_check(self):
        response = self.admin_client.patch(
            f'/api/cours/{self.existing.id}/', {'intitule': 'Maths avancées'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_write_forbidden_for_intervenant_and_etudiant(self):
        response = self.intervenant_client.post('/api/cours/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.etudiant_client.post('/api/cours/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_intervenant_sees_only_own_cours(self):
        Cours.objects.create(
            intitule='Anglais', classe=self.classe2, salle=self.salle2, intervenant=self.intervenant2,
            debut=make_aware(datetime(2026, 9, 10, 14)), fin=make_aware(datetime(2026, 9, 10, 15)),
        )
        response = self.intervenant_client.get('/api/cours/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.existing.id)

    def test_etudiant_sees_only_own_classe_cours(self):
        Cours.objects.create(
            intitule='Anglais', classe=self.classe2, salle=self.salle2, intervenant=self.intervenant2,
            debut=make_aware(datetime(2026, 9, 10, 14)), fin=make_aware(datetime(2026, 9, 10, 15)),
        )
        response = self.etudiant_client.get('/api/cours/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.existing.id)

    def test_admin_can_filter_by_classe_salle_intervenant_and_date(self):
        response = self.admin_client.get(f'/api/cours/?classe={self.classe.id}')
        self.assertEqual(len(response.data), 1)

        response = self.admin_client.get('/api/cours/?date=2026-09-10')
        self.assertEqual(len(response.data), 1)

        response = self.admin_client.get('/api/cours/?date=2026-09-11')
        self.assertEqual(len(response.data), 0)
