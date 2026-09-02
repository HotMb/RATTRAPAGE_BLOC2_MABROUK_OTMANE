from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Classe, Salle, Intervenant, Etudiant
from .permissions import IsAdminOrReadOnly, IsAdmin
from .serializers import (
    RoleTokenObtainPairSerializer, ClasseSerializer, SalleSerializer,
    IntervenantSerializer, EtudiantSerializer,
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
