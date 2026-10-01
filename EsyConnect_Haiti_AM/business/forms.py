from django import forms
from django.core.exceptions import ValidationError
from .models import Business, Review, BusinessGallery, Department, Ville, Quartier, Category

class BusinessRegistrationForm(forms.ModelForm):
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
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Non biznis ou an...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'departement_obj': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'departement-select'
            }),
            'ville_obj': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'ville-select'
            }),
            'quartier_obj': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'quartier-select'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Adres konplè (Ri, nimewo...)'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '19.7594',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '-72.2497',
                'step': 'any'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
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
            'placeholder': 'Pataje eksperyans ou ak biznis sa a...'
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
