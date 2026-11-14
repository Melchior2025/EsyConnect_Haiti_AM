from django.urls import path
from . import views

app_name = 'business'

urlpatterns = [
    path('', views.home, name='home'),
    path('businesses/', views.business_list, name='business_list'),
    path('business/<int:business_id>/', views.business_detail, name='business_detail'),
    path('business/<int:business_id>/detail/', views.business_detail, name='detail'),
    path('business/<int:business_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('business/<int:business_id>/edit/', views.edit_business, name='edit'),
    path('business/<int:business_id>/delete/', views.delete_business, name='delete'),
    path('business/<int:business_id>/gallery/', views.manage_gallery, name='manage_gallery'),
    path('business/<int:business_id>/manage-gallery/', views.manage_gallery, name='manage_gallery_alt'),
    path('business/<int:business_id>/gallery/<int:image_id>/delete/', views.delete_gallery_image, name='delete_gallery_image'),
    path('business/<int:business_id>/delete-image/<int:image_id>/', views.delete_gallery_image, name='delete_gallery_image_alt'),
    path('business/<int:business_id>/review/', views.review, name='review'),
    path('business/<int:business_id>/track/<str:action_type>/', views.track_click, name='track_click'),
    path('categories/', views.categories, name='categories'),
    path('category/<int:category_id>/', views.category_detail, name='category'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_general, name='contact_general'),
    path('search/', views.search, name='search'),
    path('register/', views.register_business, name='register'),
    path('register-business/', views.register_business, name='register_business'),
    path('favorites/', views.favorites, name='favorites'),
    path('departements/', views.departments, name='departments'),
    path('department/<slug:slug>/', views.department_detail, name='department_detail'),
    path('ville/<slug:slug>/', views.ville_detail, name='ville_detail'),
    path('pricing/', views.pricing_plans, name='pricing'),
    path('subscription/checkout/<slug:plan_code>/', views.checkout_subscription, name='checkout_subscription'),
    path('donate/', views.submit_donation, name='submit_donation'),
    path('ajax/load-villes/', views.load_villes, name='load_villes'),
    path('ajax/load-quartiers/', views.load_quartiers, name='load_quartiers'),
]