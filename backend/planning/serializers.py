from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Classe, Salle


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['username'] = self.user.username
        return data


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = ['id', 'nom', 'niveau']


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ['id', 'nom_ou_numero', 'capacite', 'type']
