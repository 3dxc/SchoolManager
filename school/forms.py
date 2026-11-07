from django import forms
from .models import Etablissement, AnneeScolaire, Classe, Matiere


class EtablissementForm(forms.ModelForm):
    class Meta:
        model = Etablissement
        fields = ['nom', 'adresse', 'telephone', 'email', 'logo']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Complexe Scolaire d\'Excellence de Bamako'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Quartier du Fleuve, Rue 310, Porte 45, Bamako - Mali'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +223 20 22 28 36'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: contact@schoolmanager.ml'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['etablissement', 'libelle', 'date_debut', 'date_fin', 'statut']
        widgets = {
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'libelle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2025-2026'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['nom', 'grande_section', 'niveau', 'annee_scolaire', 'capacite_max']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Terminale TSE 1, 10ème CG2, 6ème A, L2 Informatique'}),
            'grande_section': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'capacite_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 45'}),
        }


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom', 'coefficient', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mathématiques, Physique-Chimie, Français'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 4'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Objectifs d\'apprentissage et programme du cours...'}),
        }
