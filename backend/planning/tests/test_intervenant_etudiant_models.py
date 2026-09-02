from django.test import TestCase
from planning.models import User, Classe, Intervenant, Etudiant


class IntervenantEtudiantModelTests(TestCase):
    def test_create_intervenant_linked_to_user(self):
        user = User.objects.create_user(username='jdupont', password='pass1234', role=User.Role.INTERVENANT)
        intervenant = Intervenant.objects.create(user=user, nom='Dupont', prenom='Jean', email='j.dupont@efficom.fr')
        self.assertEqual(user.intervenant, intervenant)

    def test_create_etudiant_linked_to_user_and_classe(self):
        classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        user = User.objects.create_user(username='amartin', password='pass1234', role=User.Role.ETUDIANT)
        etudiant = Etudiant.objects.create(user=user, nom='Martin', prenom='Alice', email='a.martin@efficom.fr', classe=classe)
        self.assertEqual(user.etudiant, etudiant)
        self.assertEqual(etudiant.classe, classe)
