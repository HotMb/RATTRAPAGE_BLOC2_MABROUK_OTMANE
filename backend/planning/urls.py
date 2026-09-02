from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RoleTokenObtainPairView, ClasseViewSet, SalleViewSet

router = DefaultRouter()
router.register('classes', ClasseViewSet, basename='classe')
router.register('salles', SalleViewSet, basename='salle')

urlpatterns = [
    path('auth/login/', RoleTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('', include(router.urls)),
]
