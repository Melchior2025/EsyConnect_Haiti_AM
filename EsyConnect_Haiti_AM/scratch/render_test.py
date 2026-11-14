import os, django, sys
os.chdir('EsyConnect_Haiti_AM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EsyConnect_Haiti_AM.settings')
django.setup()
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from users.views import business_dashboard
User = get_user_model()
if not User.objects.exists():
    print('No users in database')
    sys.exit(0)
user = User.objects.first()
request = RequestFactory().get('/users/business-dashboard/')
request.user = user
response = business_dashboard(request)
print('Status:', response.status_code)
print('Context keys:', list(response.context_data.keys()))

