from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Utilisateur personnalisé avec rôle intégré."""

    ROLE_ADMIN = 'admin'
    ROLE_DIRECTION = 'direction'
    ROLE_ENSEIGNANT = 'enseignant'
    ROLE_PAIEMENT = 'paiement'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrateur'),
        (ROLE_DIRECTION, 'Personnel de direction'),
        (ROLE_ENSEIGNANT, 'Enseignant'),
        (ROLE_PAIEMENT, 'Personnel paiement'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_DIRECTION,
        verbose_name='Rôle',
    )
    telephone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ── Helpers de rôle ───────────────────────────────────────────────────────
    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_direction(self):
        return self.role in (self.ROLE_ADMIN, self.ROLE_DIRECTION) or self.is_superuser

    @property
    def is_enseignant(self):
        return self.role == self.ROLE_ENSEIGNANT

    @property
    def is_paiement(self):
        return self.role == self.ROLE_PAIEMENT
