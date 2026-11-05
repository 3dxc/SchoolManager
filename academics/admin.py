from django.contrib import admin
from .models import Enseignant, Affectation, Note


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'specialite', 'telephone', 'email')
    search_fields = ('nom', 'prenom', 'specialite')


@admin.register(Affectation)
class AffectationAdmin(admin.ModelAdmin):
    list_display = ('enseignant', 'matiere', 'classe', 'annee_scolaire')
    list_filter = ('annee_scolaire', 'classe')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('inscription', 'matiere', 'periode', 'valeur', 'saisie_par')
    list_filter = ('periode', 'matiere')
    search_fields = ('inscription__eleve__nom',)
