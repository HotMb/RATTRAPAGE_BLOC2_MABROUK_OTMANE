from django.test import TestCase
from planning.models import Classe, Salle


class ClasseSalleModelTests(TestCase):
    def test_create_classe(self):
        classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        self.assertEqual(str(classe), 'BTS SIO 1')

    def test_create_salle(self):
        salle = Salle.objects.create(nom_ou_numero='A101', capacite=30, type='TD')
        self.assertEqual(salle.capacite, 30)
        self.assertEqual(str(salle), 'A101')
