import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EsyConnect_Haiti_AM.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from users.views import dashboard, business_dashboard

factory = RequestFactory()
request = factory.get('/users/dashboard/')
user = User.objects.first()

if user:
    request.user = user
    print(f"Testing with user: {user}")
    
    # Test dashboard
    try:
        response = dashboard(request)
        print("Dashboard rendered successfully.")
    except Exception as e:
        import traceback
        print("Error rendering dashboard:")
        traceback.print_exc()

    # Test business_dashboard
    request = factory.get('/users/business_dashboard/')
    request.user = user
    try:
        response = business_dashboard(request)
        print("Business Dashboard rendered successfully.")
    except Exception as e:
        import traceback
        print("Error rendering business_dashboard:")
        traceback.print_exc()
else:
    print("No users in db, creating one...")
    user = User.objects.create(username='testuser', email='test@example.com')
    request.user = user
    try:
        response = dashboard(request)
        print("Dashboard rendered successfully.")
    except Exception as e:
        import traceback
        print("Error rendering dashboard:")
        traceback.print_exc()
