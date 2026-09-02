from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from planning.models import User, Classe, Salle, Intervenant, Etudiant, Cours

DEMO_PASSWORD = 'Demo1234!'


class Command(BaseCommand):
    help = 'Seed demo accounts and sample scheduling data.'

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username='admin', defaults={'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password(DEMO_PASSWORD)
            admin.save()

        classe, _ = Classe.objects.get_or_create(nom='BTS SIO 1', defaults={'niveau': 'BTS1'})
        salle, _ = Salle.objects.get_or_create(nom_ou_numero='A101', defaults={'capacite': 30, 'type': 'TD'})

        interv_user, created = User.objects.get_or_create(
            username='intervenant1', defaults={'role': User.Role.INTERVENANT},
        )
        if created:
            interv_user.set_password(DEMO_PASSWORD)
            interv_user.save()
        intervenant, _ = Intervenant.objects.get_or_create(
            user=interv_user, defaults={'nom': 'Dupont', 'prenom': 'Jean', 'email': 'j.dupont@efficom.fr'},
        )

        etu_user, created = User.objects.get_or_create(
            username='etudiant1', defaults={'role': User.Role.ETUDIANT},
        )
        if created:
            etu_user.set_password(DEMO_PASSWORD)
            etu_user.save()
        Etudiant.objects.get_or_create(
            user=etu_user, defaults={'nom': 'Martin', 'prenom': 'Alice', 'email': 'a.martin@efficom.fr', 'classe': classe},
        )

        Cours.objects.get_or_create(
            intitule='Mathématiques', classe=classe, salle=salle, intervenant=intervenant,
            debut=make_aware(datetime(2026, 9, 15, 9)), fin=make_aware(datetime(2026, 9, 15, 10)),
        )
        Cours.objects.get_or_create(
            intitule='Anglais', classe=classe, salle=salle, intervenant=intervenant,
            debut=make_aware(datetime(2026, 9, 15, 10)), fin=make_aware(datetime(2026, 9, 15, 11)),
        )

        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready. Accounts: admin/{DEMO_PASSWORD}, intervenant1/{DEMO_PASSWORD}, etudiant1/{DEMO_PASSWORD}'
        ))
