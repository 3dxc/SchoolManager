import uuid
from django.db import models
from django.core.exceptions import ValidationError
from students.models import Inscription


class Absence(models.Model):
    MOTIF_JUSTIFIE = 'justifie'
    MOTIF_NON_JUSTIFIE = 'non_justifie'
    MOTIF_CHOICES = [
        (MOTIF_JUSTIFIE, 'Justifiée'),
        (MOTIF_NON_JUSTIFIE, 'Non justifiée'),
    ]

    inscription = models.ForeignKey(
        Inscription, on_delete=models.CASCADE,
        related_name='absences', verbose_name='Inscription'
    )
    date = models.DateField(verbose_name='Date')
    motif = models.CharField(max_length=15, choices=MOTIF_CHOICES, default=MOTIF_NON_JUSTIFIE, verbose_name='Motif')
    description = models.TextField(blank=True, verbose_name='Description / Justification')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Absence'
        verbose_name_plural = 'Absences'
        ordering = ['-date']
        unique_together = [('inscription', 'date')]

    def __str__(self):
        return f"{self.inscription.eleve} — {self.date} ({self.get_motif_display()})"


class FraisScolaire(models.Model):
    """Définit le montant total des frais de scolarité pour une inscription."""
    inscription = models.OneToOneField(
        Inscription, on_delete=models.CASCADE,
        related_name='frais_scolaire', verbose_name='Inscription'
    )
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant total (FCFA)')
    date_echeance = models.DateField(blank=True, null=True, verbose_name='Date d\'échéance')
    observations = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Frais scolaires'
        verbose_name_plural = 'Frais scolaires'

    def __str__(self):
        return f"Frais — {self.inscription}"

    def clean(self):
        if self.montant_total is not None and self.montant_total < 0:
            raise ValidationError({'montant_total': "Le montant ne peut pas être négatif."})


class Paiement(models.Model):
    MODE_ESPECES = 'especes'
    MODE_VIREMENT = 'virement'
    MODE_MOBILE = 'mobile_money'
    MODE_CHEQUE = 'cheque'
    MODE_CHOICES = [
        (MODE_ESPECES, 'Espèces'),
        (MODE_VIREMENT, 'Virement bancaire'),
        (MODE_MOBILE, 'Mobile Money'),
        (MODE_CHEQUE, 'Chèque'),
    ]

    inscription = models.ForeignKey(
        Inscription, on_delete=models.CASCADE,
        related_name='paiements', verbose_name='Inscription'
    )
    reference = models.CharField(max_length=50, unique=True, verbose_name='Référence')
    montant = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant (FCFA)')
    date = models.DateField(verbose_name='Date du paiement')
    mode_paiement = models.CharField(max_length=20, choices=MODE_CHOICES, default=MODE_ESPECES, verbose_name='Mode de paiement')
    recu_par = models.CharField(max_length=100, blank=True, verbose_name='Reçu par')
    observations = models.TextField(blank=True, verbose_name='Observations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date']

    def __str__(self):
        return f"Paiement {self.reference} — {self.inscription.eleve} — {self.montant} FCFA"

    def clean(self):
        if self.montant is not None and self.montant <= 0:
            raise ValidationError({'montant': "Le montant doit être positif."})

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
