import uuid
from django.db import models
from django.core.exceptions import ValidationError
from school.models import Classe, AnneeScolaire


class Eleve(models.Model):
    SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

    matricule = models.CharField(max_length=20, unique=True, verbose_name='Matricule')
    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    date_naissance = models.DateField(verbose_name='Date de naissance')
    lieu_naissance = models.CharField(max_length=100, blank=True, verbose_name='Lieu de naissance')
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, default='M', verbose_name='Sexe')
    adresse = models.TextField(blank=True, verbose_name='Adresse')
    photo = models.ImageField(upload_to='eleves/', blank=True, null=True, verbose_name='Photo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Élève'
        verbose_name_plural = 'Élèves'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"

    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"

    @staticmethod
    def generer_matricule():
        """Génère un matricule unique basé sur l'année et un UUID."""
        from django.utils import timezone
        prefix = timezone.now().year
        suffix = uuid.uuid4().hex[:6].upper()
        return f"{prefix}-{suffix}"


class Parent(models.Model):
    RELATION_CHOICES = [
        ('pere', 'Père'),
        ('mere', 'Mère'),
        ('tuteur', 'Tuteur / Tutrice'),
        ('grand_parent', 'Grand-parent'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    telephone = models.CharField(max_length=20, verbose_name='Téléphone')
    telephone2 = models.CharField(max_length=20, blank=True, verbose_name='Téléphone 2')
    email = models.EmailField(blank=True, verbose_name='Email')
    profession = models.CharField(max_length=100, blank=True, verbose_name='Profession')
    adresse = models.TextField(blank=True, verbose_name='Adresse')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Parent / Tuteur'
        verbose_name_plural = 'Parents / Tuteurs'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class ResponsableEleve(models.Model):
    """Table intermédiaire M2M entre Parent et Eleve avec la nature de la relation."""
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='responsables', verbose_name='Élève')
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='eleves_a_charge', verbose_name='Parent')
    relation = models.CharField(
        max_length=20,
        choices=Parent.RELATION_CHOICES,
        default='tuteur',
        verbose_name='Relation',
    )
    est_contact_principal = models.BooleanField(default=False, verbose_name='Contact principal')

    class Meta:
        verbose_name = 'Responsable élève'
        verbose_name_plural = 'Responsables élèves'
        unique_together = [('eleve', 'parent')]

    def __str__(self):
        return f"{self.parent} → {self.eleve} ({self.get_relation_display()})"


class Inscription(models.Model):
    STATUT_ACTIF = 'actif'
    STATUT_TRANSFERE = 'transfere'
    STATUT_EXCLU = 'exclu'
    STATUT_DIPLOME = 'diplome'
    STATUT_ANNULE = 'annule'

    STATUT_CHOICES = [
        (STATUT_ACTIF, 'Actif'),
        (STATUT_TRANSFERE, 'Transféré'),
        (STATUT_EXCLU, 'Exclu'),
        (STATUT_DIPLOME, 'Diplômé'),
        (STATUT_ANNULE, 'Annulé'),
    ]

    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='inscriptions', verbose_name='Élève')
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name='inscriptions', verbose_name='Classe')
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.PROTECT,
        related_name='inscriptions', verbose_name='Année scolaire'
    )
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default=STATUT_ACTIF, verbose_name='Statut')
    date_inscription = models.DateField(auto_now_add=True, verbose_name='Date d\'inscription')
    frais_scolarite = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=150000, verbose_name='Frais de scolarité (FCFA)'
    )
    observations = models.TextField(blank=True, verbose_name='Observations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        ordering = ['-annee_scolaire__date_debut', 'eleve__nom']
        # Un élève ne peut être actif que dans une seule classe par année scolaire
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'annee_scolaire'],
                condition=models.Q(statut='actif'),
                name='unique_inscription_active_par_annee',
            )
        ]

    def __str__(self):
        return f"{self.eleve} — {self.classe} ({self.annee_scolaire.libelle})"

    def clean(self):
        # Vérifier que la classe appartient à l'année scolaire
        if self.classe and self.annee_scolaire:
            if self.classe.annee_scolaire != self.annee_scolaire:
                raise ValidationError(
                    "La classe sélectionnée n'appartient pas à l'année scolaire choisie."
                )

    @property
    def montant_paye(self):
        return self.paiements.aggregate(total=models.Sum('montant'))['total'] or 0

    @property
    def solde_restant(self):
        return self.frais_scolarite - self.montant_paye

    @property
    def est_a_jour(self):
        return self.solde_restant <= 0
