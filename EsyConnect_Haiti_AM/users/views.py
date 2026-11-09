from django.shortcuts import render, get_object_or_404, redirect
from django.db import OperationalError
from django.contrib.auth.decorators import login_required
from business.models import Business, SubscriptionPlan, Subscription, PaymentTransaction
from .models import UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm

@login_required
def business_dashboard(request):
    try:
        businesses = Business.objects.filter(owner=request.user)
        stats = {
            'total_businesses': businesses.count(),
            'active_businesses': businesses.filter(is_active=True).count(),
            'pending_businesses': businesses.filter(is_active=False).count(),
            'premium_businesses': businesses.filter(is_pro=True).count(),
        }
    except OperationalError:
        businesses = []
        stats = {
            'total_businesses': 0,
            'active_businesses': 0,
            'pending_businesses': 0,
            'premium_businesses': 0,
        }

    context = {
        'businesses': businesses,
        'stats': stats,
        'monthly_labels': [],
        'monthly_views': [],
        'cat_labels': [],
        'cat_data': [],
    }
    return render(request, 'users/business_dashboard.html', context)

@login_required
def delete_business(request, business_id):
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    if request.method == 'POST':
        business.delete()
    return redirect('users:business_dashboard')

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def dashboard(request):
    try:
        businesses = Business.objects.filter(owner=request.user)
        stats = {
            'total_businesses': businesses.count(),
            'total_views': sum(b.view_count for b in businesses),
            'total_leads': sum(b.contacts_count for b in businesses),
            'total_reviews': 0, # Placeholder
        }
    except OperationalError:
        businesses = []
        stats = {
            'total_businesses': 0,
            'total_views': 0,
            'total_leads': 0,
            'total_reviews': 0,
        }

    context = {
        'businesses': businesses,
        'stats': stats,
        'monthly_labels': [],
        'monthly_views': [],
        'monthly_leads': [],
        'zone_labels': [],
        'zone_data': [],
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {
        'user_profile': profile,
    }
    return render(request, 'users/profile.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    from .forms import UserRegisterForm
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def subscription_dashboard(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order', 'price')
    active_subscription = Subscription.objects.filter(user=request.user, status='active').order_by('-created_at').first()
    pending_subscription = Subscription.objects.filter(user=request.user, status='pending').order_by('-created_at').first()
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')[:10]

    context = {
        'plans': plans,
        'active_subscription': active_subscription,
        'pending_subscription': pending_subscription,
        'transactions': transactions,
    }
    return render(request, 'users/subscription.html', context)

@login_required
def reviews_dashboard(request):
    return render(request, 'users/reviews.html')

@login_required
def export_businesses_csv(request):
    from django.http import HttpResponse
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="businesses.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Catégorie', 'Vues', 'Actif', 'PRO'])
    
    try:
        businesses = Business.objects.filter(owner=request.user)
        for b in businesses:
            writer.writerow([b.name, b.category.name if b.category else '', b.view_count, b.is_active, b.is_pro])
    except Exception:
        pass
        
    return response