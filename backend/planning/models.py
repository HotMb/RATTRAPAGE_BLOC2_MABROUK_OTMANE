from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        INTERVENANT = 'INTERVENANT', 'Intervenant'
        ETUDIANT = 'ETUDIANT', 'Étudiant'

    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f'{self.username} ({self.role})'


class Classe(models.Model):
    nom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


class Salle(models.Model):
    nom_ou_numero = models.CharField(max_length=50)
    capacite = models.PositiveIntegerField()
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.nom_ou_numero
