from django import forms
from .models import Eleve, Parent, ResponsableEleve, Inscription
from school.models import Classe, AnneeScolaire


class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = ['matricule', 'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'adresse', 'photo']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2026-0042 (auto-généré si vide)'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Traoré, Coulibaly, Diarra'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Aminata, Mamadou, Ousmane'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bamako, Sikasso, Ségou, Mopti'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Badalabougou Rue 45, Porte 12, Bamako'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['matricule'].initial = Eleve.generer_matricule()


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['nom', 'prenom', 'telephone', 'telephone2', 'email', 'profession', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Traoré'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Oumar'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +223 76 12 34 56'}),
            'telephone2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +223 66 98 76 54'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: parent.oumar@malimail.ml'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Enseignant, Cadre bancaire, Ingénieur'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: ACI 2000, Commune IV, Bamako'}),
        }


class ResponsableEleveForm(forms.ModelForm):
    class Meta:
        model = ResponsableEleve
        fields = ['parent', 'relation', 'est_contact_principal']
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'relation': forms.Select(attrs={'class': 'form-select'}),
            'est_contact_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['eleve', 'classe', 'annee_scolaire', 'statut', 'frais_scolarite', 'observations']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'frais_scolarite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 150000 (FCFA)'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Inscription annuelle standard, dossier complet, réduction fratrie 10%'}),
        }
