from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Classe, Salle
from .permissions import IsAdminOrReadOnly
from .serializers import RoleTokenObtainPairSerializer, ClasseSerializer, SalleSerializer


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
