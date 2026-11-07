from django import forms
from .models import Absence, FraisScolaire, Paiement


class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ['inscription', 'date', 'motif', 'description']
        widgets = {
            'inscription': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motif': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Certificat médical fourni, motif familial légitime...'}),
        }


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['inscription', 'reference', 'montant', 'date', 'mode_paiement', 'recu_par', 'observations']
        widgets = {
            'inscription': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PAIE-2026-0042 (auto-générée si vide)'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '500', 'placeholder': 'Ex: 50000 (FCFA)'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'recu_par': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fatoumata Koné (Caisse Principale)'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Scolarité 1er trimestre / Tranche 1 - Reçu remis au parent'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reference'].required = False
