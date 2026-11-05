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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['inscription', 'reference', 'montant', 'date', 'mode_paiement', 'recu_par', 'observations']
        widgets = {
            'inscription': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-générée si vide'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '500'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'recu_par': forms.TextInput(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reference'].required = False
