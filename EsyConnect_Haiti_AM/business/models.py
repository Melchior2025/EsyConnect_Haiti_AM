from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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

    @property
    def image(self):
        return self.cover_image or self.logo

    logo = models.ImageField(upload_to="business_logos/", default="default_logo.png", blank=True)
    # Optional address for display in listings and map popups
    address = models.CharField(max_length=255, blank=True, null=True)
    cover_image = models.ImageField(upload_to="business_covers/", blank=True, null=True)
    # Optional geographic coordinates for map display
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude (decimal degrees)")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude (decimal degrees)")
    # Social media links
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    
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


class Favorite(models.Model):
    """User favorites for businesses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoris'
        unique_together = ('user', 'business')

    def __str__(self):
        return f"{self.user.username} - {self.business.name}"


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


# ==========================================
# 4. Modèl Abònman ak Peman (Paid Accounts & Subscriptions)
# ==========================================

class SubscriptionPlan(models.Model):
    """Plan abònman disponib pou biznis (Basic, Pro Mensuel, Pro Annuel, VIP)."""
    name = models.CharField(max_length=100, verbose_name="Nom du plan")
    code = models.SlugField(max_length=50, unique=True, help_text="Idantifyan inik (ex: free, pro_monthly, pro_yearly, vip)")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Prix")
    currency = models.CharField(
        max_length=10,
        default="USD",
        choices=[("USD", "USD ($)"), ("HTG", "HTG (Gourdes)")],
        verbose_name="Devise"
    )
    duration_days = models.PositiveIntegerField(
        default=30,
        help_text="Nombre de jours de validité (0 pour gratuit / permanent)"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    features = models.TextField(
        blank=True,
        help_text="Liste des fonctionnalités (une par ligne ou séparée par virgule)"
    )
    max_businesses = models.PositiveIntegerField(default=1, verbose_name="Max entreprises autorisées")
    badge_text = models.CharField(max_length=50, blank=True, default="PRO", verbose_name="Texte du badge")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_default = models.BooleanField(default=False, verbose_name="Plan par défaut (Gratuit)")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Plan d'abonnement"
        verbose_name_plural = "Plans d'abonnement"
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"

    def get_features_list(self):
        """Retourne la liste des fonctionnalités sous forme de liste Python."""
        if not self.features:
            return []
        lines = [line.strip() for line in self.features.replace(',', '\n').split('\n') if line.strip()]
        return lines


class Subscription(models.Model):
    """Abònman aktif oswa istorik yon itilizatè / biznis."""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('pending', 'En attente de paiement / validation'),
        ('expired', 'Expiré'),
        ('canceled', 'Annulé'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name="Utilisateur")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions', verbose_name="Plan")
    business = models.ForeignKey(
        Business,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions',
        verbose_name="Entreprise spécifique (optionnel)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Date de début")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    auto_renew = models.BooleanField(default=False, verbose_name="Renouvellement automatique")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.get_status_display()})"

    @property
    def is_valid(self):
        """Verifie si abònman an aktif e li poko ekspire."""
        if self.status != 'active':
            return False
        if not self.end_date:
            return True  # Plan gratuit / permanent
        return self.end_date >= timezone.now()

    def activate(self):
        """Aktive abònman an, kalkile dat fen an, epi mete biznis itilizatè a PRO."""
        self.status = 'active'
        self.start_date = timezone.now()
        if self.plan.duration_days > 0:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        else:
            self.end_date = None
        self.save()

        # Mete biznis yo PRO si plan an se yon plan peyan
        if self.plan.price > 0 or self.plan.code != 'free':
            if self.business:
                self.business.is_pro = True
                self.business.save(update_fields=['is_pro'])
            else:
                Business.objects.filter(owner=self.user).update(is_pro=True)

    def expire_or_cancel(self, new_status='expired'):
        """Dezaktive abònman an epi mete ajou estati biznis yo."""
        self.status = new_status
        self.save(update_fields=['status'])
        # Verifye si itilizatè a pa gen yon lòt abònman aktif
        other_active = Subscription.objects.filter(
            user=self.user,
            status='active'
        ).exclude(id=self.id)
        valid_subs = [s for s in other_active if s.is_valid and (s.plan.price > 0 or s.plan.code != 'free')]
        if not valid_subs:
            Business.objects.filter(owner=self.user).update(is_pro=False)


class PaymentTransaction(models.Model):
    """Tranzaksyon peman pou yon abònman (MonCash, Natcash, Stripe, Virement, elatriye)."""
    METHOD_CHOICES = [
        ('moncash', 'MonCash (Digicel)'),
        ('natcash', 'Natcash (Natcom)'),
        ('stripe', 'Carte Bancaire / Stripe'),
        ('bank_transfer', 'Virement / Dépôt Bancaire (Sogebank/Unibank)'),
        ('cash', 'Espèces / En personne'),
        ('admin', 'Manuel (Admin)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Confirmé / Validé'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name="Abonnement lié"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions', verbose_name="Utilisateur")
    business = models.ForeignKey(
        Business,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_transactions',
        verbose_name="Entreprise"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    currency = models.CharField(max_length=10, default="USD", verbose_name="Devise")
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES, verbose_name="Méthode de paiement")
    transaction_reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Référence / ID de transaction",
        help_text="Ex: Kòd konfimasyon MonCash / Natcash oswa referans depo labank"
    )
    sender_phone_or_account = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro de l'expéditeur",
        help_text="Numéro téléphone MonCash/Natcash ou nom du compte expéditeur"
    )
    proof_image = models.ImageField(
        upload_to="payment_proofs/",
        blank=True,
        null=True,
        verbose_name="Preuve de paiement (Screenshot / Reçu)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes / Commentaires")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de confirmation")

    class Meta:
        verbose_name = "Transaction de paiement"
        verbose_name_plural = "Transactions de paiement"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_reference} - {self.amount} {self.currency} ({self.get_status_display()})"

    def confirm_and_activate(self):
        """Konfime tranzaksyon an epi aktive abònman ki asosye a."""
        self.status = 'completed'
        self.confirmed_at = timezone.now()
        self.save()
        if self.subscription:
            self.subscription.activate()


class Donation(models.Model):
    """Sipò kominotè ak donasyon pou ti antreprenè Ayisyen yo."""
    donor_name = models.CharField(max_length=150, blank=True, default="Anonyme", verbose_name="Nom du donateur")
    donor_email = models.EmailField(blank=True, null=True, verbose_name="Email")
    donor_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Téléphone / WhatsApp")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    currency = models.CharField(
        max_length=10,
        default="HTG",
        choices=[("HTG", "HTG (Gourdes)"), ("USD", "USD ($)")],
        verbose_name="Devise"
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('moncash', 'MonCash (Digicel)'),
            ('natcash', 'Natcash (Natcom)'),
            ('bank_transfer', 'Virement / Dépôt Bancaire'),
            ('card', 'Carte Bancaire / En ligne'),
        ],
        default='moncash',
        verbose_name="Méthode de paiement"
    )
    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Référence transaction"
    )
    message = models.TextField(blank=True, null=True, verbose_name="Message de soutien")
    status = models.CharField(
        max_length=20,
        default='completed',
        choices=[
            ('pending', 'En attente'),
            ('completed', 'Reçu / Confirmé'),
        ],
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Donation de solidarité"
        verbose_name_plural = "Donations de solidarité"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.donor_name} - {self.amount} {self.currency} ({self.created_at.strftime('%d/%m/%Y')})"

