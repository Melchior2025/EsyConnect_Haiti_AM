from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les messages d'erreur
        self.fields['username'].error_messages = {
            'required': 'Le nom d\'utilisateur est requis',
            'invalid': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et @/./+/-/_',
            'unique': 'Ce nom d\'utilisateur est déjà pris',
        }
        self.fields['email'].error_messages = {
            'required': 'L\'email est requis',
            'invalid': 'Veuillez entrer une adresse email valide',
        }
        self.fields['password1'].error_messages = {
            'required': 'Le mot de passe est requis',
            'min_length': 'Le mot de passe doit contenir au moins 6 caractères',
        }
        self.fields['password2'].error_messages = {
            'required': 'La confirmation du mot de passe est requise',
        }

    class Meta:
        model = User
        fields = ['username', 'email']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-esy-blue-600 font-medium'}),
            'email': forms.EmailInput(attrs={'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-esy-blue-600 font-medium'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-esy-blue-600 font-medium'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-esy-blue-600 font-medium'}),
        }

from .models import UserProfile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-esy-blue-600 font-medium', 'placeholder': '+509 ...'})
        }
