from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Classe, Salle, Intervenant, Etudiant


class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Rôle', {'fields': ('role',)}),
    )
    list_display = ('username', 'role', 'is_staff', 'is_active')


admin.site.register(User, UserAdmin)
admin.site.register(Classe)
admin.site.register(Salle)
admin.site.register(Intervenant)
admin.site.register(Etudiant)
