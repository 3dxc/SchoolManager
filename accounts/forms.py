from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import CustomUser


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Identifiant',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identifiant', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
    )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'etablissement', 'telephone')
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class CustomUserChangeForm(UserChangeForm):
    password = None  # On ne touche pas au mot de passe ici

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'etablissement', 'telephone', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
