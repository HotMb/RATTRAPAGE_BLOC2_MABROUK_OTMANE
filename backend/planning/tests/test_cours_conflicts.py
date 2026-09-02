from django.test import TestCase
from django.utils.timezone import make_aware
from datetime import datetime

from planning.models import User, Classe, Salle, Intervenant, Cours, find_conflicting_cours


def dt(y, m, d, h, mi=0):
    return make_aware(datetime(y, m, d, h, mi))


class ConflictDetectionTests(TestCase):
    def setUp(self):
        self.classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        self.classe2 = Classe.objects.create(nom='BTS SIO 2', niveau='BTS2')
        self.salle = Salle.objects.create(nom_ou_numero='A101', capacite=30, type='TD')
        self.salle2 = Salle.objects.create(nom_ou_numero='A102', capacite=30, type='TD')

        user1 = User.objects.create_user(username='interv1', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant = Intervenant.objects.create(user=user1, nom='Dupont', prenom='Jean', email='j@efficom.fr')
        user2 = User.objects.create_user(username='interv2', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant2 = Intervenant.objects.create(user=user2, nom='Martin', prenom='Alice', email='a@efficom.fr')

        self.existing = Cours.objects.create(
            intitule='Maths', classe=self.classe, salle=self.salle, intervenant=self.intervenant,
            debut=dt(2026, 9, 10, 9), fin=dt(2026, 9, 10, 10),
        )

    def test_no_conflict_for_unrelated_slot(self):
        result = find_conflicting_cours(
            salle=self.salle2, classe=self.classe2, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 14), fin=dt(2026, 9, 10, 15),
        )
        self.assertIsNone(result)

    def test_consecutive_slot_is_not_a_conflict(self):
        result = find_conflicting_cours(
            salle=self.salle, classe=self.classe2, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 10), fin=dt(2026, 9, 10, 11),
        )
        self.assertIsNone(result)

    def test_salle_conflict_detected(self):
        result = find_conflicting_cours(
            salle=self.salle, classe=self.classe2, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30),
        )
        self.assertIsNotNone(result)
        ressource, cours = result
        self.assertEqual(ressource, 'la salle')
        self.assertEqual(cours, self.existing)

    def test_intervenant_conflict_detected(self):
        result = find_conflicting_cours(
            salle=self.salle2, classe=self.classe2, intervenant=self.intervenant,
            debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30),
        )
        self.assertIsNotNone(result)
        ressource, cours = result
        self.assertEqual(ressource, "l'intervenant")
        self.assertEqual(cours, self.existing)

    def test_classe_conflict_detected(self):
        result = find_conflicting_cours(
            salle=self.salle2, classe=self.classe, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30),
        )
        self.assertIsNotNone(result)
        ressource, cours = result
        self.assertEqual(ressource, 'la classe')

    def test_excludes_self_when_editing(self):
        result = find_conflicting_cours(
            salle=self.salle, classe=self.classe, intervenant=self.intervenant,
            debut=dt(2026, 9, 10, 9), fin=dt(2026, 9, 10, 10),
            exclude_pk=self.existing.pk,
        )
        self.assertIsNone(result)
