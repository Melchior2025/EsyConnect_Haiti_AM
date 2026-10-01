import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EsyConnect_Haiti_AM.settings')
django.setup()

from django.urls import get_resolver

def show_urls(resolver, prefix=''):
    for p in resolver.url_patterns:
        path = prefix + str(p.pattern)
        if hasattr(p, 'url_patterns'):
            show_urls(p, path)
        else:
            name = getattr(p, 'name', '') or ''
            print(f'{path} [{name}]')

show_urls(get_resolver())
