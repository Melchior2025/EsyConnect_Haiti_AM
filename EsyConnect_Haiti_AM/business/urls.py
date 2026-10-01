from django.urls import path
from . import views

app_name = 'business'  # <-- Fòk liy sa a la tou nan business/urls.py

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_general, name='contact_general'),
    path('search/', views.search, name='search'),
    path('favorites/', views.favorites, name='favorites'),
    path('business/<int:business_id>/', views.detail, name='detail'),
    path('business/<int:business_id>/edit/', views.edit, name='edit'),
    path('business/<int:business_id>/delete/', views.delete, name='delete'),
    path('business/<int:business_id>/manage-gallery/', views.manage_gallery, name='manage_gallery'),
    path('business/<int:business_id>/delete-image/<int:image_id>/', views.delete_gallery_image, name='delete_gallery_image'),
    path('business/<int:business_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('business/<int:business_id>/review/', views.review, name='review'),
    path('register/', views.register_business, name='register'),
    path('register-business/', views.register_business, name='register_business'),
    path('category/<int:category_id>/', views.category, name='category'),
    path('department/<slug:slug>/', views.department_detail, name='department_detail'),
    path('departements/', views.departments, name='departments'),
    path('ville/<slug:slug>/', views.ville_detail, name='ville_detail'),
]