from django import forms
from django.conf import settings
from .models import Enseignant, Affectation, Note


class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = ['nom', 'prenom', 'specialite', 'telephone', 'email', 'user']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Coulibaly'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bakary'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mathématiques, Sciences Physiques'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +223 70 11 22 33'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: b.coulibaly@schoolmanager.ml'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
        }


class AffectationForm(forms.ModelForm):
    class Meta:
        model = Affectation
        fields = ['enseignant', 'matiere', 'classe', 'annee_scolaire']
        widgets = {
            'enseignant': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['inscription', 'matiere', 'periode', 'valeur', 'commentaire']
        widgets = {
            'inscription': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'periode': forms.Select(attrs={'class': 'form-select'}),
            'valeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '20', 'placeholder': 'Note / 20 (ex: 15.5)'}),
            'commentaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Très bon travail, persévérez / Devoir N°1'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si l'utilisateur est enseignant, filtrer les inscriptions selon ses affectations
        if user and hasattr(user, 'enseignant_profil'):
            enseignant = user.enseignant_profil
            from students.models import Inscription
            affectations = Affectation.objects.filter(enseignant=enseignant)
            classes = affectations.values_list('classe', flat=True)
            annees = affectations.values_list('annee_scolaire', flat=True)
            self.fields['inscription'].queryset = Inscription.objects.filter(
                classe__in=classes, annee_scolaire__in=annees, statut='actif'
            ).select_related('eleve', 'classe')
            matieres = affectations.values_list('matiere', flat=True)
            from school.models import Matiere
            self.fields['matiere'].queryset = Matiere.objects.filter(pk__in=matieres)
