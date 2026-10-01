from django.db import models
from django.contrib.auth.models import User

# 1. Modèl Jeografi (Lokalizasyon)
class Department(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"

    def __str__(self):
        return self.name

    @property
    def slug(self):
        from django.utils.text import slugify
        return slugify(self.name)

    @property
    def nom(self):
        return self.name


class Ville(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='villes')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"

    def __str__(self):
        return self.name

    @property
    def slug(self):
        from django.utils.text import slugify
        return slugify(self.name)

    @property
    def nom(self):
        return self.name


class Quartier(models.Model):
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='quartiers')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"

    def __str__(self):
        return self.name


# 2. Modèl Kategori ak Antrepriz
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: fas fa-store")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name


class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")
    name = models.CharField(max_length=150, verbose_name="Nom de l'entreprise")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="businesses")
    # Use field names that match existing migrations/database (departement_obj, ville_obj, quartier_obj)
    departement_obj = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='businesses', verbose_name='Département')
    ville_obj = models.ForeignKey(Ville, on_delete=models.SET_NULL, null=True, blank=True, related_name='businesses', verbose_name='Ville')
    quartier_obj = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True, related_name='businesses', verbose_name='Quartier')
    # Backwards-compatible properties for code expecting `department`, `ville`, `quartier`
    @property
    def department(self):
        return self.departement_obj

    @property
    def ville(self):
        return self.ville_obj

    @property
    def quartier(self):
        return self.quartier_obj
    logo = models.ImageField(upload_to="business_logos/", default="default_logo.png", blank=True)
    # Optional address for display in listings and map popups
    address = models.CharField(max_length=255, blank=True, null=True)
    cover_image = models.ImageField(upload_to="business_covers/", blank=True, null=True)
    # Optional geographic coordinates for map display
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude (decimal degrees)")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude (decimal degrees)")
    
    # Metrik ak Statut
    view_count = models.PositiveIntegerField(default=0)
    whatsapp_clicks = models.PositiveIntegerField(default=0)
    call_count = models.PositiveIntegerField(default=0)

    @property
    def contacts_count(self):
        # Return number of related leads as a fallback when no DB column exists
        try:
            return self.leads.count()
        except Exception:
            return 0

    @property
    def phone(self):
        try:
            return self.owner.profile.phone
        except Exception:
            return None

    @property
    def whatsapp(self):
        return self.phone

    @property
    def email(self):
        try:
            return self.owner.email
        except Exception:
            return None

    @property
    def description(self):
        cat_name = self.category.name if self.category else "Services"
        ville_name = self.ville_obj.name if self.ville_obj else "Haïti"
        return f"{self.name} - {cat_name} disponible à {ville_name}."
    is_active = models.BooleanField(default=True, verbose_name="Est actif")
    is_pro = models.BooleanField(default=False, verbose_name="Compte PRO")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_average_rating(self):
        reviews = Review.objects.filter(business=self)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0.0

    def get_rating_count(self):
        return Review.objects.filter(business=self).count()


# 2. Review model – stores customer ratings for a Business
class Review(models.Model):
    """Simple review linking a user (optional) to a business with a rating and comment."""
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Entreprise',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='business_reviews',
        verbose_name='Utilisateur',
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='Note',
    )
    comment = models.TextField(blank=True, null=True, verbose_name='Commentaire')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']

    def __str__(self):
        user_part = f"{self.user.username}" if self.user else "Anonyme"
        return f"{user_part} – {self.rating}/5 pour {self.business.name}"

# 3. Galerik, Tracking, ak Konfigirasyon
class BusinessGallery(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="business_gallery/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Galerie d'entreprise"
        verbose_name_plural = "Galeries d'entreprises"


class LeadTracking(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='leads')
    action_type = models.CharField(max_length=50, help_text="ex: appel, whatsapp, email", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Suivi de prospect"
        verbose_name_plural = "Suivis de prospects"


class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=100, default="EsyConnect")
    contact_email = models.EmailField(blank=True, null=True)
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Configuration du site"
        verbose_name_plural = "Configurations du site"

    def __str__(self):
        return self.site_name