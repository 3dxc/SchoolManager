from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings


class Etablissement(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom')
    adresse = models.TextField(blank=True, verbose_name='Adresse')
    telephone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.EmailField(blank=True, verbose_name='Email')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name='Logo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Établissement'
        verbose_name_plural = 'Établissements'

    def __str__(self):
        return self.nom


class AnneeScolaire(models.Model):
    STATUT_EN_COURS = 'en_cours'
    STATUT_TERMINEE = 'terminee'
    STATUT_A_VENIR = 'a_venir'
    STATUT_CHOICES = [
        (STATUT_EN_COURS, 'En cours'),
        (STATUT_TERMINEE, 'Terminée'),
        (STATUT_A_VENIR, 'À venir'),
    ]

    etablissement = models.ForeignKey(
        Etablissement, on_delete=models.CASCADE,
        related_name='annees_scolaires', verbose_name='Établissement'
    )
    libelle = models.CharField(max_length=20, verbose_name='Libellé', help_text='Ex: 2024-2025')
    date_debut = models.DateField(verbose_name='Date de début')
    date_fin = models.DateField(verbose_name='Date de fin')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default=STATUT_A_VENIR, verbose_name='Statut')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Année scolaire'
        verbose_name_plural = 'Années scolaires'
        ordering = ['-date_debut']
        unique_together = [('etablissement', 'libelle')]

    def __str__(self):
        return f"{self.libelle} — {self.etablissement.nom}"

    def clean(self):
        if self.date_debut and self.date_fin and self.date_debut >= self.date_fin:
            raise ValidationError({'date_fin': "La date de fin doit être postérieure à la date de début."})


class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    coefficient = models.PositiveSmallIntegerField(default=1, verbose_name='Coefficient')
    description = models.TextField(blank=True, verbose_name='Description')

    class Meta:
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Classe(models.Model):
    # ══ Grandes Sections (Cycles d'enseignement de la pédagogie malienne) ══
    GRANDE_SECTION_MATERNELLE = 'maternelle'
    GRANDE_SECTION_FONDAMENTAL_1 = 'fondamental_1'
    GRANDE_SECTION_FONDAMENTAL_2 = 'fondamental_2'
    GRANDE_SECTION_LYCEE = 'lycee'
    GRANDE_SECTION_LICENCE = 'licence'
    GRANDE_SECTION_MASTER = 'master'
    GRANDE_SECTION_DOCTORAT = 'doctorat'
    GRANDE_SECTION_AUTRE = 'autre'

    GRANDE_SECTION_CHOICES = [
        (GRANDE_SECTION_MATERNELLE, 'Maternelle (Préscolaire)'),
        (GRANDE_SECTION_FONDAMENTAL_1, '1er Cycle Fondamental (1ère à 6ème Année)'),
        (GRANDE_SECTION_FONDAMENTAL_2, '2nd Cycle Fondamental (7ème à 9ème Année - DEF)'),
        (GRANDE_SECTION_LYCEE, 'Lycée (10ème, 11ème & Terminale - BAC)'),
        (GRANDE_SECTION_LICENCE, 'Enseignement Supérieur — Licence (L1, L2, L3)'),
        (GRANDE_SECTION_MASTER, 'Enseignement Supérieur — Master (M1, M2)'),
        (GRANDE_SECTION_DOCTORAT, 'Enseignement Supérieur — Doctorat'),
        (GRANDE_SECTION_AUTRE, 'Autre / Spécifique'),
    ]

    # ══ Niveaux conformes aux standards de la pédagogie malienne ══
    NIVEAU_CHOICES = [
        ('Maternelle (Préscolaire)', (
            ('mat_ps', 'Petite Section (PS)'),
            ('mat_ms', 'Moyenne Section (MS)'),
            ('mat_gs', 'Grande Section (GS)'),
        )),
        ('1er Cycle Fondamental (École Fondamentale 1)', (
            ('fond_1', '1ère Année Fondamentale'),
            ('fond_2', '2ème Année Fondamentale'),
            ('fond_3', '3ème Année Fondamentale'),
            ('fond_4', '4ème Année Fondamentale'),
            ('fond_5', '5ème Année Fondamentale'),
            ('fond_6', '6ème Année Fondamentale (CEP)'),
        )),
        ('2nd Cycle Fondamental (Collège malien - DEF)', (
            ('fond_7', '7ème Année Fondamentale'),
            ('fond_8', '8ème Année Fondamentale'),
            ('fond_9', '9ème Année Fondamentale (DEF)'),
        )),
        ('Lycée (Enseignement Secondaire - BAC)', (
            ('lyc_10', '10ème Année (Tronc Commun)'),
            ('lyc_11', '11ème Année (11e Lettres / Sciences)'),
            ('lyc_tle', 'Terminale (TSE, TSExp, TSS, TAL - BAC)'),
        )),
        ('Enseignement Supérieur — Licence', (
            ('lic_1', 'Licence 1 (L1)'),
            ('lic_2', 'Licence 2 (L2)'),
            ('lic_3', 'Licence 3 (L3)'),
        )),
        ('Enseignement Supérieur — Master', (
            ('mast_1', 'Master 1 (M1)'),
            ('mast_2', 'Master 2 (M2)'),
        )),
        ('Enseignement Supérieur — Doctorat', (
            ('doc_1', 'Doctorat 1ère Année (D1)'),
            ('doc_2', 'Doctorat 2ème Année (D2)'),
            ('doc_3', 'Doctorat 3ème Année (D3+)'),
        )),
        ('Historique & Autres', (
            ('3e', '3ème'),
            ('4e', '4ème'),
            ('5e', '5ème'),
            ('autre', 'Autre'),
        ))
    ]

    nom = models.CharField(max_length=50, verbose_name='Nom', help_text='Ex: 10ème CG1, Terminale TSE, 6ème A')
    grande_section = models.CharField(
        max_length=30,
        choices=GRANDE_SECTION_CHOICES,
        default=GRANDE_SECTION_LYCEE,
        verbose_name='Grande Section / Cycle',
        help_text='Cycle officiel du système éducatif malien'
    )
    niveau = models.CharField(max_length=30, choices=NIVEAU_CHOICES, default='autre', verbose_name='Niveau')
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.CASCADE,
        related_name='classes', verbose_name='Année scolaire'
    )
    capacite_max = models.PositiveSmallIntegerField(default=40, verbose_name='Capacité maximale')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['grande_section', 'niveau', 'nom']
        unique_together = [('nom', 'annee_scolaire')]

    def __str__(self):
        return f"{self.nom} — {self.get_niveau_display()} ({self.annee_scolaire.libelle})"

    def save(self, *args, **kwargs):
        # Synchronisation automatique de la grande section en fonction du niveau
        if self.niveau.startswith('mat_'):
            self.grande_section = self.GRANDE_SECTION_MATERNELLE
        elif self.niveau in ('fond_1', 'fond_2', 'fond_3', 'fond_4', 'fond_5', 'fond_6'):
            self.grande_section = self.GRANDE_SECTION_FONDAMENTAL_1
        elif self.niveau in ('fond_7', 'fond_8', 'fond_9', '3e', '4e', '5e'):
            self.grande_section = self.GRANDE_SECTION_FONDAMENTAL_2
        elif self.niveau.startswith('lyc_'):
            self.grande_section = self.GRANDE_SECTION_LYCEE
        elif self.niveau.startswith('lic_'):
            self.grande_section = self.GRANDE_SECTION_LICENCE
        elif self.niveau.startswith('mast_'):
            self.grande_section = self.GRANDE_SECTION_MASTER
        elif self.niveau.startswith('doc_'):
            self.grande_section = self.GRANDE_SECTION_DOCTORAT
        super().save(*args, **kwargs)

    @property
    def nb_eleves(self):
        return self.inscriptions.filter(statut='actif').count()


class Campus(models.Model):
    """
    Modèle Campus & Secrétariat : permet à l'administration de modifier l'adresse,
    le téléphone, les coordonnées GPS pour la carte Leaflet, les horaires et les consignes
    sans devoir modifier le code source.
    """
    nom = models.CharField(max_length=200, default="Campus & Secrétariat", verbose_name="Nom du campus")
    etablissement = models.ForeignKey(
        Etablissement, on_delete=models.CASCADE,
        related_name="campus_set", null=True, blank=True,
        verbose_name="Établissement rattaché"
    )
    adresse = models.TextField(
        default="Place de la Liberté - BP 71, Bamako - Mali",
        verbose_name="Adresse complète"
    )
    telephone = models.CharField(
        max_length=50, default="+223 20 23 10 35",
        verbose_name="Téléphone d'accueil / Standard"
    )
    telephone_mobile = models.CharField(
        max_length=50, default="+223 76 00 00 00", blank=True,
        verbose_name="Téléphone direct / Urgences"
    )
    email = models.EmailField(
        default="contact@schoolmanager.ml",
        verbose_name="Courriel officiel"
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, default=12.639200,
        verbose_name="Latitude GPS"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, default=-7.998200,
        verbose_name="Longitude GPS"
    )
    zoom_carte = models.PositiveSmallIntegerField(
        default=15, verbose_name="Niveau de zoom de la carte (1 à 19)"
    )
    lien_inscription = models.CharField(
        max_length=255, blank=True, default="",
        verbose_name="Lien externe d'inscription (optionnel)",
        help_text="Laissez vide pour utiliser le formulaire d'inscription standard du système."
    )
    horaires = models.TextField(
        default="Du Lundi au Vendredi : 07h30 - 16h30\nSamedi : 08h00 - 12h00\nDimanche : Fermé",
        verbose_name="Horaires d'ouverture"
    )
    consignes_acces = models.TextField(
        default="Entrée principale située Place de la Liberté. Présentation obligatoire d'un badge ou d'une pièce d'identité à l'accueil pour tout visiteur.",
        verbose_name="Consignes d'accès et sécurité"
    )
    actif = models.BooleanField(default=True, verbose_name="Campus principal affiché sur le tableau de bord")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Campus & Secrétariat"
        verbose_name_plural = "Campus & Secrétariats"

    def __str__(self):
        return f"{self.nom} — {self.adresse[:40]}"

    @property
    def telephone_digits(self):
        """Format nettoyé pour les liens href='tel:...' sur mobile."""
        return "".join(c for c in self.telephone if c.isdigit() or c == '+')

    @property
    def mobile_digits(self):
        """Format nettoyé pour le mobile."""
        return "".join(c for c in self.telephone_mobile if c.isdigit() or c == '+')

    @property
    def itineraire_url(self):
        """Lien direct vers l'application de navigation GPS (Google Maps / Apple Maps / OSM)."""
        return f"https://www.google.com/maps/dir/?api=1&destination={self.latitude},{self.longitude}"


class SignalementProbleme(models.Model):
    """
    Modèle de signalement : remplace le simple texte statique par un véritable
    système d'enregistrement et de suivi des demandes et problèmes par l'administration.
    """
    TYPE_TECHNIQUE = 'technique'
    TYPE_ACCES = 'acces'
    TYPE_CAMPUS = 'campus'
    TYPE_PEDAGOGIQUE = 'pedagogique'
    TYPE_AUTRE = 'autre'
    TYPE_CHOICES = [
        (TYPE_TECHNIQUE, 'Problème technique / Affichage de la carte'),
        (TYPE_ACCES, 'Accès / Connexion au portail'),
        (TYPE_CAMPUS, 'Locaux / Campus / Stationnement / Accès'),
        (TYPE_PEDAGOGIQUE, 'Question administrative / Inscription'),
        (TYPE_AUTRE, 'Autre signalement ou réclamation'),
    ]

    STATUT_NOUVEAU = 'nouveau'
    STATUT_EN_COURS = 'en_cours'
    STATUT_RESOLU = 'resolu'
    STATUT_REJETE = 'rejete'
    STATUT_CHOICES = [
        (STATUT_NOUVEAU, 'Nouveau / En attente'),
        (STATUT_EN_COURS, 'En cours de traitement'),
        (STATUT_RESOLU, 'Traité & Résolu'),
        (STATUT_REJETE, 'Classé sans suite'),
    ]

    campus = models.ForeignKey(
        Campus, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='signalements', verbose_name="Campus concerné"
    )
    type_probleme = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_TECHNIQUE,
        verbose_name="Type de problème"
    )
    nom = models.CharField(max_length=150, verbose_name="Nom complet / Auteur")
    email = models.EmailField(blank=True, verbose_name="Adresse courriel")
    telephone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone de contact")
    message = models.TextField(verbose_name="Description détaillée du problème")
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default=STATUT_NOUVEAU,
        verbose_name="Statut du traitement"
    )
    notes_admin = models.TextField(
        blank=True, verbose_name="Notes administratives de suivi / Traitement"
    )
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='signalements_traites', verbose_name="Traité par"
    )
    date_signalement = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    date_resolution = models.DateTimeField(null=True, blank=True, verbose_name="Date de clôture / résolution")

    class Meta:
        verbose_name = "Signalement de problème"
        verbose_name_plural = "Signalements de problèmes"
        ordering = ['-date_signalement']

    def __str__(self):
        return f"[{self.get_statut_display()}] {self.get_type_probleme_display()} — {self.nom} ({self.date_signalement.strftime('%d/%m/%Y')})"

