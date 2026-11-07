from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


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
