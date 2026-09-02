from datetime import datetime, timedelta

from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.timezone import make_aware

from .models import User, Classe, Salle, Intervenant, Etudiant, Cours
from .permissions import IsAdminOrReadOnly, IsAdmin
from .serializers import (
    RoleTokenObtainPairSerializer, ClasseSerializer, SalleSerializer,
    IntervenantSerializer, EtudiantSerializer, CoursSerializer,
)


class RoleTokenObtainPairView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer


class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all().order_by('nom')
    serializer_class = ClasseSerializer
    permission_classes = [IsAdminOrReadOnly]


class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all().order_by('nom_ou_numero')
    serializer_class = SalleSerializer
    permission_classes = [IsAdminOrReadOnly]


class IntervenantViewSet(viewsets.ModelViewSet):
    queryset = Intervenant.objects.select_related('user').all().order_by('nom')
    serializer_class = IntervenantSerializer
    permission_classes = [IsAdmin]


class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.select_related('user', 'classe').all().order_by('nom')
    serializer_class = EtudiantSerializer
    permission_classes = [IsAdmin]


class CoursViewSet(viewsets.ModelViewSet):
    serializer_class = CoursSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Cours.objects.select_related('classe', 'salle', 'intervenant').order_by('debut')

        if user.role == User.Role.INTERVENANT:
            qs = qs.filter(intervenant__user=user)
        elif user.role == User.Role.ETUDIANT:
            etudiant = getattr(user, 'etudiant', None)
            qs = qs.filter(classe=etudiant.classe) if etudiant else qs.none()

        date_str = self.request.query_params.get('date')
        if date_str:
            day_start = make_aware(datetime.strptime(date_str, '%Y-%m-%d'))
            qs = qs.filter(debut__gte=day_start, debut__lt=day_start + timedelta(days=1))

        if user.role == User.Role.ADMIN:
            for param, field in (('classe', 'classe_id'), ('salle', 'salle_id'), ('intervenant', 'intervenant_id')):
                value = self.request.query_params.get(param)
                if value:
                    qs = qs.filter(**{field: value})

        return qs
