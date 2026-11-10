from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'etablissement', 'is_active')
    list_filter = ('role', 'etablissement', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations SchoolManager', {'fields': ('role', 'etablissement', 'telephone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations SchoolManager', {'fields': ('role', 'etablissement', 'telephone')}),
    )
