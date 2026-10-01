import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EsyConnect_Haiti_AM.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

user = User.objects.first()
print(f"Using user: {user.username}")

c = Client()
c.force_login(user)

# Test ALL URLs
pages = [
    # Public pages
    ('/fr/', 'Home'),
    ('/fr/search/', 'Search'),
    ('/fr/categories/', 'Categories'),
    ('/fr/about/', 'About'),
    ('/fr/contact/', 'Contact'),
    ('/fr/departements/', 'Departments'),
    # Auth pages
    ('/fr/users/login/', 'Login'),
    ('/fr/users/register/', 'Register'),
    ('/fr/users/password-reset/', 'Password Reset'),
    # Protected pages
    ('/fr/users/dashboard/', 'Dashboard'),
    ('/fr/users/business-dashboard/', 'Business Dashboard'),
    ('/fr/users/reviews/', 'Reviews Dashboard'),
    ('/fr/users/subscription/', 'Subscription'),
    ('/fr/users/profile/', 'Profile'),
    ('/fr/users/edit-profile/', 'Edit Profile'),
    ('/fr/favorites/', 'Favorites'),
    # Business actions
    ('/fr/register/', 'Register Business'),
    ('/fr/business/1/', 'Business Detail'),
    ('/fr/business/1/edit/', 'Edit Business'),
    ('/fr/business/1/manage-gallery/', 'Manage Gallery'),
]

print("\n" + "="*60)
print(f"{'URL':<45} {'Name':<20} {'Status'}")
print("="*60)

errors = []
for url, name in pages:
    try:
        r = c.get(url, SERVER_NAME='127.0.0.1')
        status = r.status_code
        status_text = 'OK' if status == 200 else f'!! {status}'
        print(f"{url:<45} {name:<20} {status_text}")
        if status >= 400:
            content = r.content.decode('utf-8', errors='replace')
            if 'TemplateSyntaxError' in content:
                errors.append((url, name, 'TemplateSyntaxError'))
            elif 'TemplateDoesNotExist' in content:
                errors.append((url, name, 'TemplateDoesNotExist'))
            elif status == 500:
                errors.append((url, name, 'Server Error 500'))
    except Exception as e:
        print(f"{url:<45} {name:<20} FAIL {e}")
        errors.append((url, name, str(e)))

print("\n" + "="*60)
if errors:
    print(f"\n[X] {len(errors)} ERRORS FOUND:")
    for url, name, err in errors:
        print(f"  - {name} ({url}): {err}")
else:
    print("\n[OK] ALL PAGES WORKING!")
print("="*60)
