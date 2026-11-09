from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='business:home'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('business-dashboard/', views.business_dashboard, name='business_dashboard'),
    path('business/<int:business_id>/delete/', views.delete_business, name='delete_business'),
    path('delete-business/<int:business_id>/', views.delete_business, name='delete_business_alt'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('subscription/', views.subscription_dashboard, name='subscription_dashboard'),
    path('subscription-alt/', views.subscription_dashboard, name='subscription'),
    path('reviews/', views.reviews_dashboard, name='reviews_dashboard'),
    path('reviews-alt/', views.reviews_dashboard, name='reviews'),
    path('export-businesses-csv/', views.export_businesses_csv, name='export_businesses_csv'),
]