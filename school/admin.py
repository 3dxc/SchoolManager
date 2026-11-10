from django.contrib import admin
from .models import Etablissement, AnneeScolaire, Classe, Matiere, Campus, SignalementProbleme


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse_courte', 'telephone', 'email', 'latitude', 'longitude', 'actif')
    list_filter = ('actif', 'etablissement')
    search_fields = ('nom', 'adresse', 'telephone', 'email')
    fieldsets = (
        ("Informations Principales", {
            'fields': ('nom', 'etablissement', 'actif')
        }),
        ("Coordonnées & Contact Direct", {
            'fields': ('adresse', 'telephone', 'telephone_mobile', 'email')
        }),
        ("Géolocalisation & Carte Interactive (Leaflet / OSM)", {
            'fields': ('latitude', 'longitude', 'zoom_carte'),
            'description': "Ces coordonnées GPS déterminent l'emplacement exact du marqueur et le centrage de la carte interactive sur le tableau de bord."
        }),
        ("Inscriptions & Modalités", {
            'fields': ('lien_inscription',),
            'description': "Laissez vide pour utiliser le formulaire d'inscription standard du portail."
        }),
        ("Horaires d'Ouverture & Consignes d'Accès", {
            'fields': ('horaires', 'consignes_acces')
        }),
    )

    def adresse_courte(self, obj):
        return obj.adresse[:45] + "..." if len(obj.adresse) > 45 else obj.adresse
    adresse_courte.short_description = "Adresse"


@admin.register(SignalementProbleme)
class SignalementProblemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_probleme', 'nom', 'email', 'telephone', 'statut', 'date_signalement')
    list_filter = ('statut', 'type_probleme', 'date_signalement', 'campus')
    search_fields = ('nom', 'email', 'telephone', 'message', 'notes_admin')
    readonly_fields = ('date_signalement',)
    actions = ['marquer_resolu', 'marquer_en_cours']

    fieldsets = (
        ("Détails du Signalement", {
            'fields': ('type_probleme', 'campus', 'nom', 'email', 'telephone', 'message', 'date_signalement')
        }),
        ("Suivi Administratif", {
            'fields': ('statut', 'notes_admin', 'traite_par', 'date_resolution')
        }),
    )

    def marquer_resolu(self, request, queryset):
        from django.utils import timezone
        queryset.update(statut=SignalementProbleme.STATUT_RESOLU, date_resolution=timezone.now())
        self.message_user(request, "Les signalements sélectionnés ont été marqués comme Résolus.")
    marquer_resolu.short_description = "Marquer comme Résolu(s)"

    def marquer_en_cours(self, request, queryset):
        queryset.update(statut=SignalementProbleme.STATUT_EN_COURS)
        self.message_user(request, "Les signalements sélectionnés ont été passés En cours de traitement.")
    marquer_en_cours.short_description = "Marquer En cours de traitement"


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email')
    search_fields = ('nom',)


@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etablissement', 'date_debut', 'date_fin', 'statut')
    list_filter = ('statut', 'etablissement')


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'niveau', 'annee_scolaire', 'capacite_max')
    list_filter = ('niveau', 'annee_scolaire')
    search_fields = ('nom',)


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'coefficient')
    search_fields = ('nom',)
