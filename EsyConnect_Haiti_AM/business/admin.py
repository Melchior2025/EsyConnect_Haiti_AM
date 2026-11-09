from django.contrib import admin
from django.utils import timezone
from .models import (
    Category, Business, Department, Ville, Quartier, SiteConfiguration,
    Review, BusinessGallery, Favorite, LeadTracking,
    SubscriptionPlan, Subscription, PaymentTransaction, Donation
)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'currency', 'duration_days', 'max_businesses', 'badge_text', 'is_active', 'is_default', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'is_default', 'currency')
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'business', 'status', 'start_date', 'end_date', 'is_valid_badge', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('user__username', 'user__email', 'business__name')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['activate_selected_subscriptions', 'expire_selected_subscriptions']

    @admin.display(description="Valide", boolean=True)
    def is_valid_badge(self, obj):
        return obj.is_valid

    @admin.action(description="Activer les abonnements sélectionnés (et passer les biznis en PRO)")
    def activate_selected_subscriptions(self, request, queryset):
        count = 0
        for sub in queryset:
            sub.activate()
            count += 1
        self.message_user(request, f"{count} abonnement(s) activé(s) avec succès.")

    @admin.action(description="Expirer/Annuler les abonnements sélectionnés")
    def expire_selected_subscriptions(self, request, queryset):
        count = 0
        for sub in queryset:
            sub.expire_or_cancel('expired')
            count += 1
        self.message_user(request, f"{count} abonnement(s) marqués comme expirés.")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'user', 'amount', 'currency', 'payment_method', 'status', 'created_at', 'confirmed_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_reference', 'sender_phone_or_account', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'confirmed_at')
    actions = ['confirm_and_activate_transactions']

    @admin.action(description="Valider et Activer l'abonnement associé")
    def confirm_and_activate_transactions(self, request, queryset):
        count = 0
        for tx in queryset:
            if tx.status != 'completed':
                tx.confirm_and_activate()
                count += 1
        self.message_user(request, f"{count} transaction(s) validée(s) et abonnement(s) activé(s).")


admin.site.register(Category)
admin.site.register(Business)
admin.site.register(Department)
admin.site.register(Ville)
admin.site.register(Quartier)
admin.site.register(SiteConfiguration)
admin.site.register(Review)
admin.site.register(BusinessGallery)
admin.site.register(Favorite)
admin.site.register(LeadTracking)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'amount', 'currency', 'payment_method', 'transaction_reference', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('donor_name', 'donor_email', 'donor_phone', 'transaction_reference')

