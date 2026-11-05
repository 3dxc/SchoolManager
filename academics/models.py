from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from school.models import Classe, Matiere, AnneeScolaire
from students.models import Inscription


class Enseignant(models.Model):
    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    specialite = models.CharField(max_length=100, verbose_name='Spécialité')
    telephone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.EmailField(blank=True, verbose_name='Email')
    # Lien optionnel vers un compte utilisateur enseignant
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='enseignant_profil',
        verbose_name='Compte utilisateur',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"


class Affectation(models.Model):
    """Lie un enseignant à une matière pour une classe et une année scolaire données."""
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, related_name='affectations', verbose_name='Enseignant')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='affectations', verbose_name='Matière')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='affectations', verbose_name='Classe')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='affectations', verbose_name='Année scolaire')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Affectation'
        verbose_name_plural = 'Affectations'
        unique_together = [('enseignant', 'matiere', 'classe', 'annee_scolaire')]

    def __str__(self):
        return f"{self.enseignant} — {self.matiere} — {self.classe} ({self.annee_scolaire.libelle})"


class Note(models.Model):
    PERIODE_CHOICES = getattr(settings, 'PERIODES', [
        ('T1', 'Trimestre 1'),
        ('T2', 'Trimestre 2'),
        ('T3', 'Trimestre 3'),
    ])

    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, related_name='notes', verbose_name='Inscription')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='notes', verbose_name='Matière')
    periode = models.CharField(max_length=5, choices=PERIODE_CHOICES, verbose_name='Période')
    valeur = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Note')
    commentaire = models.CharField(max_length=200, blank=True, verbose_name='Commentaire')
    saisie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notes_saisies', verbose_name='Saisie par',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['inscription__eleve__nom', 'matiere__nom', 'periode']
        unique_together = [('inscription', 'matiere', 'periode')]

    def __str__(self):
        return f"{self.inscription.eleve} — {self.matiere} — {self.periode}: {self.valeur}"

    def clean(self):
        note_max = getattr(settings, 'NOTE_MAX', 20)
        note_min = getattr(settings, 'NOTE_MIN', 0)
        if self.valeur is not None:
            if self.valeur < note_min or self.valeur > note_max:
                raise ValidationError({'valeur': f"La note doit être comprise entre {note_min} et {note_max}."})
        # La matière doit être affectée à la classe de l'inscription
        if self.inscription and self.matiere:
            classe = self.inscription.classe
            annee = self.inscription.annee_scolaire
            if not Affectation.objects.filter(matiere=self.matiere, classe=classe, annee_scolaire=annee).exists():
                raise ValidationError({'matiere': "Cette matière n'est pas affectée à cette classe pour cette année scolaire."})
