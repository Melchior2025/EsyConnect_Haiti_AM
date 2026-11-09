from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Enpòtasyon dirèk views yo
from business import views as business_views

# 1. URL san prefiks lang (Tout demand AJAX yo dwe rete la)
urlpatterns = [
    path('', business_views.home, name='home'),
    
    # URL pou chanje lang (set_language)
    path('i18n/', include('django.conf.urls.i18n')),

    # AJAX pou chaje vil ak katye yo
    path('ajax/load-villes/', business_views.load_villes, name='load_villes'),
    path('load_villes/', business_views.load_villes),
    path('ajax/load-quartiers/', business_views.load_quartiers, name='load_quartiers'),
    path('load_quartiers/', business_views.load_quartiers),

    # Fallback dirèk pou enskripsyon biznis ak detay biznis san namespace
    path('register/', business_views.register_business, name='register'),
    path('register-business/', business_views.register_business, name='register_business'),
    path('business/<int:business_id>/', business_views.business_detail, name='business_detail'),
    path('business/<int:business_id>/detail/', business_views.business_detail, name='detail'),
]

# 2. URL ki gen prefiks lang (e.g., /fr/, /ht/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    
    # URL pou aplikasyon business ak users ak namespace yo
    path('', include(('business.urls', 'business'), namespace='business')),
    path('users/', include(('users.urls', 'users'), namespace='users')),

    # Fallback anba prefiks lang pou 'register' ak 'business_detail' san namespace
    path('register/', business_views.register_business, name='register'),
    path('register-business/', business_views.register_business, name='register_business'),
    path('business/<int:business_id>/', business_views.business_detail, name='business_detail'),
    path('business/<int:business_id>/detail/', business_views.business_detail, name='detail'),
    
    prefix_default_language=True,
)

# Sèvi ak fichye media ak static nan devlopman
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)