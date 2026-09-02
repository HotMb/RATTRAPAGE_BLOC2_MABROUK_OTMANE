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
