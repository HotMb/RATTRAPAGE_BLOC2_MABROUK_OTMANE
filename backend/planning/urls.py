from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RoleTokenObtainPairView

urlpatterns = [
    path('auth/login/', RoleTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
]
