from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Classe, Salle, User, Intervenant, Etudiant, Cours, find_conflicting_cours


# DRF's default exception handler reads status_code off APIException subclasses directly.
class ConflictError(APIException):
    status_code = 409
    default_code = 'conflict'


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


class IntervenantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Intervenant
        fields = ['id', 'nom', 'prenom', 'email', 'username', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Cet identifiant est déjà utilisé.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=username, password=password, role=User.Role.INTERVENANT)
        return Intervenant.objects.create(user=user, **validated_data)


class EtudiantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Etudiant
        fields = ['id', 'nom', 'prenom', 'email', 'classe', 'username', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Cet identifiant est déjà utilisé.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=username, password=password, role=User.Role.ETUDIANT)
        return Etudiant.objects.create(user=user, **validated_data)


class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = ['id', 'intitule', 'classe', 'salle', 'intervenant', 'debut', 'fin']

    def validate(self, attrs):
        debut = attrs.get('debut', getattr(self.instance, 'debut', None))
        fin = attrs.get('fin', getattr(self.instance, 'fin', None))
        salle = attrs.get('salle', getattr(self.instance, 'salle', None))
        classe = attrs.get('classe', getattr(self.instance, 'classe', None))
        intervenant = attrs.get('intervenant', getattr(self.instance, 'intervenant', None))

        if debut is not None and fin is not None and fin <= debut:
            raise serializers.ValidationError(
                {'fin': "L'heure de fin doit être postérieure à l'heure de début."}
            )

        if salle and classe and intervenant and debut and fin:
            exclude_pk = self.instance.pk if self.instance else None
            conflict = find_conflicting_cours(
                salle=salle, classe=classe, intervenant=intervenant,
                debut=debut, fin=fin, exclude_pk=exclude_pk,
            )
            if conflict:
                ressource, cours_conflit = conflict
                raise ConflictError(
                    f"Conflit détecté : {ressource} est déjà occupé(e) par le cours "
                    f"« {cours_conflit.intitule} » du "
                    f"{cours_conflit.debut:%d/%m/%Y %H:%M} au {cours_conflit.fin:%d/%m/%Y %H:%M}."
                )

        return attrs
