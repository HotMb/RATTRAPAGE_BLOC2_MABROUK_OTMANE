from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Rôle', {'fields': ('role',)}),
    )
    list_display = ('username', 'role', 'is_staff', 'is_active')


admin.site.register(User, UserAdmin)
