from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RoleTokenObtainPairView, ClasseViewSet, SalleViewSet,
    IntervenantViewSet, EtudiantViewSet, CoursViewSet,
)

router = DefaultRouter()
router.register('classes', ClasseViewSet, basename='classe')
router.register('salles', SalleViewSet, basename='salle')
router.register('intervenants', IntervenantViewSet, basename='intervenant')
router.register('etudiants', EtudiantViewSet, basename='etudiant')
router.register('cours', CoursViewSet, basename='cours')

urlpatterns = [
    path('auth/login/', RoleTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('', include(router.urls)),
]
