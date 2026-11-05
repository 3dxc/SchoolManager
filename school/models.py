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
    NIVEAU_CHOICES = [
        ('6e', '6ème'),
        ('5e', '5ème'),
        ('4e', '4ème'),
        ('3e', '3ème'),
        ('2nde', 'Seconde'),
        ('1ere', 'Première'),
        ('Tle', 'Terminale'),
        ('CP', 'CP'),
        ('CE1', 'CE1'),
        ('CE2', 'CE2'),
        ('CM1', 'CM1'),
        ('CM2', 'CM2'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=50, verbose_name='Nom', help_text='Ex: 6ème A')
    niveau = models.CharField(max_length=10, choices=NIVEAU_CHOICES, default='autre', verbose_name='Niveau')
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.CASCADE,
        related_name='classes', verbose_name='Année scolaire'
    )
    capacite_max = models.PositiveSmallIntegerField(default=40, verbose_name='Capacité maximale')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['niveau', 'nom']
        unique_together = [('nom', 'annee_scolaire')]

    def __str__(self):
        return f"{self.nom} ({self.annee_scolaire.libelle})"

    @property
    def nb_eleves(self):
        return self.inscriptions.filter(statut='actif').count()
