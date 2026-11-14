from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Business, Review, BusinessGallery, Department, Ville, Quartier, Category,
    SubscriptionPlan, Subscription, PaymentTransaction, Donation
)

class BusinessRegistrationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': "Le nom de l'entreprise est obligatoire. Veuillez le saisir.",
            'max_length': "Le nom de l'entreprise ne peut pas dépasser 150 caractères.",
        },
        widget=forms.TextInput(attrs={
            'class': 'custom-input',
            'placeholder': "Ex: Altidor Auto Parts, Pharmacie Centrale, Boutique Marie...",
            'id': 'id_name',
            'autocomplete': 'organization',
        }),
        label="Nom de l'entreprise"
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        error_messages={
            'required': "Veuillez choisir une catégorie pour votre entreprise.",
            'invalid_choice': "Catégorie invalide. Veuillez en sélectionner une dans la liste.",
        },
        widget=forms.Select(attrs={
            'class': 'custom-input cursor-pointer appearance-none',
            'id': 'category-select',
        }),
        label="Catégorie"
    )
    departement_obj = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        error_messages={
            'required': "Veuillez choisir le département où se trouve votre entreprise.",
        },
        widget=forms.Select(attrs={
            'class': 'custom-input cursor-pointer appearance-none',
            'id': 'departement-select',
        }),
        label="Département"
    )
    ville_obj = forms.ModelChoiceField(
        queryset=Ville.objects.all(),
        required=True,
        error_messages={
            'required': "Veuillez choisir la ville / commune où se trouve votre entreprise.",
        },
        widget=forms.Select(attrs={
            'class': 'custom-input cursor-pointer appearance-none',
            'id': 'ville-select',
        }),
        label="Ville / Commune"
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'custom-input',
            'placeholder': "Adresse exacte (rue, numéro, quartier...)",
            'id': 'id_address',
        }),
        label="Adresse Complète"
    )
    latitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'custom-input',
            'placeholder': '19.7594',
            'step': 'any',
            'id': 'id_latitude',
        }),
        label="Latitude"
    )
    longitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'custom-input',
            'placeholder': '-72.2497',
            'step': 'any',
            'id': 'id_longitude',
        }),
        label="Longitude"
    )
    logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'id_logo',
            'onchange': "previewFileName(this, 'logo-filename')",
        }),
        label="Logo"
    )
    cover_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'id_cover_image',
            'onchange': "previewFileName(this, 'cover-filename')",
        }),
        label="Image de couverture"
    )

    class Meta:
        model = Business
        fields = [
            'name',
            'category',
            'departement_obj',
            'ville_obj',
            'quartier_obj',
            'address',
            'latitude',
            'longitude',
            'logo',
            'cover_image',
        ]
        widgets = {
            'quartier_obj': forms.Select(attrs={
                'class': 'custom-input cursor-pointer appearance-none',
                'id': 'quartier-select'
            }),
        }
        labels = {
            'name': "Nom de l'entreprise",
            'category': 'Catégorie',
            'departement_obj': 'Département',
            'ville_obj': 'Ville',
            'quartier_obj': 'Quartier',
            'address': 'Adresse',
            'latitude': 'Latitude (GPS)',
            'longitude': 'Longitude (GPS)',
            'logo': 'Logo',
            'cover_image': 'Image de couverture',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("Le nom de l'entreprise est obligatoire. Veuillez le saisir.")
        return name


class ReviewForm(forms.ModelForm):
    """Formulaire pour laisser un avis et une note sur une entreprise"""
    rating = forms.ChoiceField(
        choices=[(i, f"{i} ★") for i in range(5, 0, -1)],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent font-bold text-amber-500'
        }),
        label='Note (1-5 étoiles)'
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Partagez votre expérience avec cette entreprise...'
        }),
        label='Commentaire',
        required=False
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '')
        if comment:
            comment = comment.strip()
            if len(comment) > 1000:
                raise ValidationError('Le commentaire ne peut pas dépasser 1000 caractères.')
        return comment


class BusinessGalleryForm(forms.ModelForm):
    """Formulaire pour ajouter des images à la galerie d'une entreprise"""
    class Meta:
        model = BusinessGallery
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            })
        }
        labels = {
            'image': 'Photo'
        }


class PaymentSubmissionForm(forms.ModelForm):
    """Formulaire pou soumèt prèv peman abònman (MonCash, Natcash, Virement, elatriye)."""
    class Meta:
        model = PaymentTransaction
        fields = [
            'payment_method',
            'transaction_reference',
            'sender_phone_or_account',
            'proof_image',
            'notes',
        ]
        widgets = {
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-3.5 border border-gray-200 rounded-2xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-medium',
                'id': 'id_payment_method',
            }),
            'transaction_reference': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3.5 border border-gray-200 rounded-2xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-medium',
                'placeholder': 'Ex: MC987654321 oswa Referans Depo',
            }),
            'sender_phone_or_account': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3.5 border border-gray-200 rounded-2xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-medium',
                'placeholder': '+509 34 00 0000 oswa Non sou kont lan',
            }),
            'proof_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-dashed border-gray-300 rounded-2xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent',
                'accept': 'image/*',
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-2xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-medium',
                'placeholder': 'Nenpòt detay oswa nòt adisyonèl pou administratè a...',
            }),
        }
        labels = {
            'payment_method': 'Mwayen peman',
            'transaction_reference': 'Kòd / Referans Tranzaksyon an',
            'sender_phone_or_account': 'Nimewo telefòn oswa kont ki voye kòb la',
            'proof_image': 'Prèv peman (Kapti dekran / Foto resi)',
            'notes': 'Nòt / Remak (opsyonèl)',
        }


class DonationForm(forms.ModelForm):
    """Formulaire pou fè yon don de solidarite pou antreprenè yo."""
    class Meta:
        model = Donation
        fields = [
            'donor_name',
            'donor_email',
            'donor_phone',
            'amount',
            'currency',
            'payment_method',
            'transaction_reference',
            'message',
        ]
        widgets = {
            'donor_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Non ou (oswa kite vid pou anonim)',
            }),
            'donor_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600',
                'placeholder': 'votre.email@example.com',
            }),
            'donor_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600',
                'placeholder': '+509 34 00 0000',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600 font-bold text-lg',
                'placeholder': '1000',
                'min': '50',
            }),
            'currency': forms.Select(attrs={
                'class': 'px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 font-bold',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600 font-medium',
            }),
            'transaction_reference': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Kòd tranzaksyon MonCash/Natcash (si disponib)',
            }),
            'message': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Yon ti mo ankourajman pou antreprenè yo...',
            }),
        }


