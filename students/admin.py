from django.contrib import admin
from .models import Eleve, Parent, ResponsableEleve, Inscription


class ResponsableEleveInline(admin.TabularInline):
    model = ResponsableEleve
    extra = 1


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'date_naissance', 'sexe')
    list_filter = ('sexe',)
    search_fields = ('matricule', 'nom', 'prenom')
    inlines = [ResponsableEleveInline]


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'telephone', 'email')
    search_fields = ('nom', 'prenom', 'telephone')


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'classe', 'annee_scolaire', 'statut', 'frais_scolarite')
    list_filter = ('statut', 'annee_scolaire', 'classe')
    search_fields = ('eleve__nom', 'eleve__matricule')
