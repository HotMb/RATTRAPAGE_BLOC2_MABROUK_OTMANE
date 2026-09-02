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


class Intervenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='intervenant')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f'{self.prenom} {self.nom}'


class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='etudiant')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name='etudiants')

    def __str__(self):
        return f'{self.prenom} {self.nom}'


class Cours(models.Model):
    intitule = models.CharField(max_length=200)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name='cours')
    salle = models.ForeignKey(Salle, on_delete=models.PROTECT, related_name='cours')
    intervenant = models.ForeignKey(Intervenant, on_delete=models.PROTECT, related_name='cours')
    debut = models.DateTimeField()
    fin = models.DateTimeField()

    class Meta:
        ordering = ['debut']

    def __str__(self):
        return f'{self.intitule} ({self.debut:%d/%m/%Y %H:%M})'


def find_conflicting_cours(*, salle, classe, intervenant, debut, fin, exclude_pk=None):
    overlapping = Cours.objects.filter(debut__lt=fin, fin__gt=debut)
    if exclude_pk is not None:
        overlapping = overlapping.exclude(pk=exclude_pk)

    salle_conflict = overlapping.filter(salle=salle).first()
    if salle_conflict:
        return ('la salle', salle_conflict)

    classe_conflict = overlapping.filter(classe=classe).first()
    if classe_conflict:
        return ('la classe', classe_conflict)

    intervenant_conflict = overlapping.filter(intervenant=intervenant).first()
    if intervenant_conflict:
        return ("l'intervenant", intervenant_conflict)

    return None
