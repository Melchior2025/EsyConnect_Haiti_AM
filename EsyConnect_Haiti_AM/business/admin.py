from django.contrib import admin
from .models import Category, Business, Department, Ville, Quartier, SiteConfiguration

# Anrejistre modèl yo senp san konplikasyon pou kounye a
admin.site.register(Category)
admin.site.register(Business)
admin.site.register(Department)
admin.site.register(Ville)
admin.site.register(Quartier)
admin.site.register(SiteConfiguration)