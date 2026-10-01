def site_config(request):
    """
    Context processor pour rendre la configuration du site accessible
    dans tous les templates
    """
    try:
        # Import tardif pour éviter AppRegistryNotReady
        from .models import SiteConfiguration
        config = SiteConfiguration.get_config()
        return {
            'site_config': config,
            'hero_background': config.hero_background.url if config.hero_background else None,
            'logo': config.logo.url if config.logo else None,
            'welcome_message': config.welcome_message,
            'welcome_subtitle': config.welcome_subtitle,
            'site_title': config.site_title,
            'meta_description': config.meta_description,
            'contact_email': config.contact_email,
            'contact_phone': config.contact_phone,
            'is_maintenance_mode': config.is_maintenance_mode,
            'maintenance_message': config.maintenance_message,
        }
    except Exception:
        # Valeurs par défaut en cas d'erreur
        return {
            'site_config': None,
            'hero_background': None,
            'logo': None,
            'welcome_message': "Bienvenue sur EsyConnect Haïti",
            'welcome_subtitle': None,
            'site_title': "EsyConnect Haïti",
            'meta_description': None,
            'contact_email': None,
            'contact_phone': None,
            'is_maintenance_mode': False,
            'maintenance_message': None,
        }
