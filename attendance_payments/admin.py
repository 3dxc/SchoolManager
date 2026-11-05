from django.contrib import admin
from .models import Absence, FraisScolaire, Paiement


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('inscription', 'date', 'motif')
    list_filter = ('motif', 'date')
    search_fields = ('inscription__eleve__nom',)


@admin.register(FraisScolaire)
class FraisScolaireAdmin(admin.ModelAdmin):
    list_display = ('inscription', 'montant_total', 'date_echeance')


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('reference', 'inscription', 'montant', 'date', 'mode_paiement')
    list_filter = ('mode_paiement', 'date')
    search_fields = ('reference', 'inscription__eleve__nom')
