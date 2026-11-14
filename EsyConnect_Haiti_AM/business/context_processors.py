def site_config(request):
    """
    Context processor pour rendre la configuration du site accessible
    dans tous les templates.
    """
    try:
        from .models import SiteConfiguration
        config = SiteConfiguration.objects.first()
        if not config:
            raise ValueError("No SiteConfiguration found")
        return {
            'site_config': config,
            # hero_image (nouveau champ — anciennement hero_background)
            'hero_background': config.hero_image.url if config.hero_image else None,
            'logo': config.logo.url if config.logo else None,
            'site_name': config.site_name,
            'meta_description': config.meta_description,
            'contact_email': config.contact_email,
            'contact_phone': config.phone_number,
            'is_maintenance_mode': config.maintenance_mode,
            'facebook_url': config.facebook_url,
            'instagram_url': config.instagram_url,
            'whatsapp_number': config.whatsapp_number,
            'footer_text': config.footer_text,
            'address': config.address,
        }
    except Exception:
        return {
            'site_config': None,
            'hero_background': None,
            'logo': None,
            'site_name': 'EsyConnect Haïti',
            'meta_description': None,
            'contact_email': None,
            'contact_phone': None,
            'is_maintenance_mode': False,
            'facebook_url': None,
            'instagram_url': None,
            'whatsapp_number': None,
            'footer_text': None,
            'address': None,
        }
