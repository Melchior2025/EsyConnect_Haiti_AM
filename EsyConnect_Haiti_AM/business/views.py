from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Q, Count
import csv
from django.contrib.auth.decorators import login_required
from .models import (
    Business, Category, Favorite, Review, Department, Ville, Quartier,
    SubscriptionPlan, Subscription, PaymentTransaction, Donation
)
from .forms import BusinessRegistrationForm, ReviewForm, PaymentSubmissionForm, DonationForm

import json
import re
import urllib.parse

def home(request):
    featured_businesses = Business.objects.filter(is_active=True).select_related(
        'category', 'departement_obj', 'ville_obj', 'quartier_obj'
    ).order_by('-is_pro', '-is_verified', '-created_at')[:6]
    
    categories = Category.objects.annotate(biz_count=Count('businesses')).order_by('name')
    departments = Department.objects.all().order_by('name')
    villes = Ville.objects.all().order_by('name')

    total_businesses = Business.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_cities = Ville.objects.count()
    total_departments = Department.objects.count()

    # Temwayaj reyèl ki soti nan baz done a (4 oswa 5 zetwal)
    testimonials = Review.objects.filter(rating__gte=4).select_related('user', 'business').order_by('-created_at')[:6]

    # Données géographiques pour la carte interactive
    businesses_queryset = Business.objects.filter(is_active=True).select_related('category', 'departement_obj', 'ville_obj', 'quartier_obj')
    businesses_map = []
    for b in businesses_queryset:
        if b.latitude and b.longitude:
            logo_url = b.cover_image.url if b.cover_image else (b.logo.url if b.logo else '')
            businesses_map.append({
                'id': b.id,
                'name': b.name,
                'latitude': float(b.latitude),
                'longitude': float(b.longitude),
                'category_name': b.category.name if b.category else 'Commerce',
                'address': b.address or (f"{b.ville_obj.name}, Haïti" if b.ville_obj else "Haïti"),
                'phone': b.phone or '',
                'logo_url': logo_url,
                'is_pro': getattr(b, 'is_pro', False),
                'is_verified': getattr(b, 'is_verified', False),
                'rating': getattr(b, 'get_average_rating', lambda: 5.0)(),
                'url': reverse('business:business_detail', kwargs={'business_id': b.id}),
            })

    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order', 'price')
    donation_form = DonationForm()

    context = {
        'featured_businesses': featured_businesses,
        'categories': categories,
        'departments': departments,
        'villes': villes,
        'businesses_json': json.dumps(businesses_map),
        'map_count': len(businesses_map),
        'total_businesses': total_businesses,
        'total_categories': total_categories,
        'total_cities': total_cities,
        'total_departments': total_departments,
        'testimonials': testimonials,
        'plans': plans,
        'donation_form': donation_form,
    }
    return render(request, 'business/home.html', context)

def business_list(request):
    dept_param = (request.GET.get('department') or request.GET.get('departement', '')).strip()
    category_id = request.GET.get('category', '').strip()
    ville_param = (request.GET.get('ville') or request.GET.get('city', '')).strip()
    zone_param = (request.GET.get('zone') or request.GET.get('quartier', '')).strip()
    query = request.GET.get('q', '').strip()
    verified = request.GET.get('verified')
    premium = request.GET.get('premium')

    businesses = Business.objects.filter(is_active=True).select_related('category', 'departement_obj', 'ville_obj', 'quartier_obj')

    if dept_param:
        if dept_param.isdigit():
            businesses = businesses.filter(departement_obj_id=int(dept_param))
        else:
            businesses = businesses.filter(Q(departement_obj__name__icontains=dept_param))

    if ville_param:
        if ville_param.isdigit():
            businesses = businesses.filter(ville_obj_id=int(ville_param))
        else:
            businesses = businesses.filter(Q(ville_obj__name__icontains=ville_param))

    if zone_param:
        if zone_param.isdigit():
            zone_obj = Quartier.objects.filter(id=int(zone_param)).first()
            zone_name = zone_obj.name if zone_obj else ''
            businesses = businesses.filter(Q(quartier_obj_id=int(zone_param)) | Q(address__icontains=zone_name))
        else:
            businesses = businesses.filter(Q(quartier_obj__name__icontains=zone_param) | Q(address__icontains=zone_param))

    if category_id:
        if category_id.isdigit():
            businesses = businesses.filter(category_id=int(category_id))

    if query:
        businesses = businesses.filter(Q(name__icontains=query) | Q(address__icontains=query))

    if verified:
        businesses = businesses.filter(is_verified=True)

    if premium:
        businesses = businesses.filter(is_pro=True)

    categories = Category.objects.all()
    departments = Department.objects.all()

    if dept_param:
        if dept_param.isdigit():
            villes = Ville.objects.filter(department_id=int(dept_param))
        else:
            villes = Ville.objects.filter(department__name__icontains=dept_param)
    else:
        villes = Ville.objects.all()

    if ville_param:
        if ville_param.isdigit():
            quartiers = Quartier.objects.filter(ville_id=int(ville_param))
        else:
            quartiers = Quartier.objects.filter(ville__name__icontains=ville_param)
    else:
        quartiers = Quartier.objects.filter(ville__name__icontains="Cap")

    # Pagination (12 entreprises par page avec tri pro / date)
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(businesses.order_by('-is_pro', '-created_at'), 12)
    page_number = request.GET.get('page', 1)
    try:
        businesses_page = paginator.page(page_number)
    except PageNotAnInteger:
        businesses_page = paginator.page(1)
    except EmptyPage:
        businesses_page = paginator.page(paginator.num_pages)

    context = {
        'businesses': businesses_page,
        'total_count': paginator.count,
        'categories': categories,
        'departments': departments,
        'villes': villes,
        'quartiers': quartiers,
        'selected_department': dept_param,
        'departement_query': dept_param,
        'selected_category': category_id,
        'category_id': category_id,
        'selected_ville': ville_param,
        'ville_query': ville_param,
        'selected_zone': zone_param,
        'zone_query': zone_param,
        'query': query,
    }
    return render(request, 'business/business_list.html', context)

def categories(request):
    all_categories = Category.objects.all()
    return render(request, 'business/categories.html', {'categories': all_categories})

def about(request):
    return render(request, 'business/about.html')

def contact_general(request):
    return render(request, 'business/contact.html')

def search(request):
    return business_list(request)

@login_required
def register_business(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        category_val = post_data.get('category')
        custom_category_name = post_data.get('custom_category', '').strip()
        
        custom_cat_obj = None
        if category_val == 'autre' and custom_category_name:
            custom_cat_obj = Category.objects.filter(name__iexact=custom_category_name).first()
            if not custom_cat_obj:
                custom_cat_obj = Category.objects.create(name=custom_category_name, icon="fas fa-store")
            post_data['category'] = str(custom_cat_obj.id)
        elif category_val == 'autre':
            post_data['category'] = ''

        form = BusinessRegistrationForm(post_data, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            if custom_cat_obj:
                business.category = custom_cat_obj
            business.is_active = True
            business.save()
            messages.success(request, _("Félicitations ! Votre entreprise a été enregistrée avec succès."))
            return redirect('users:business_dashboard')
        else:
            messages.error(request, _("Veuillez vérifier les informations du formulaire."))
    else:
        form = BusinessRegistrationForm()

    categories = Category.objects.all()
    departments = Department.objects.all()
    selected_dept = form.data.get('departement_obj') if form.is_bound else None
    if selected_dept and str(selected_dept).isdigit():
        villes = Ville.objects.filter(department_id=int(selected_dept))
    else:
        villes = Ville.objects.all()

    context = {
        'form': form,
        'categories': categories,
        'departments': departments,
        'villes': villes,
    }
    return render(request, 'business/register_business.html', context)

# Coordonnées géographiques de référence pour les villes et départements d'Haïti
HAITI_COORDINATES = {
    # Ouest
    'port-au-prince': (18.5392, -72.3364),
    'delmas': (18.5478, -72.3019),
    'pétion-ville': (18.5125, -72.2853),
    'petion-ville': (18.5125, -72.2853),
    'carrefour': (18.5414, -72.3992),
    'tabarre': (18.5794, -72.2644),
    'croix-des-bouquets': (18.5772, -72.2269),
    'léogâne': (18.5111, -72.6333),
    'leogane': (18.5111, -72.6333),
    'petit-goâve': (18.4314, -72.8686),
    'petit-goave': (18.4314, -72.8686),
    # Nord
    'cap-haïtien': (19.7595, -72.2042),
    'cap-haitien': (19.7595, -72.2042),
    'limonade': (19.6739, -72.1333),
    'milot': (19.6083, -72.2167),
    'plaine-du-nord': (19.7167, -72.2667),
    'quartier-morin': (19.6958, -72.1583),
    'grande-rivière-du-nord': (19.5786, -72.1678),
    # Artibonite
    'gonaïves': (19.4475, -72.6883),
    'gonaives': (19.4475, -72.6883),
    'saint-marc': (19.1082, -72.6938),
    'verrettes': (19.0500, -72.4667),
    "petite-rivière-de-l'artibonite": (19.1333, -72.4833),
    'gros-morne': (19.6667, -72.6833),
    # Sud
    'les cayes': (18.1950, -73.7467),
    'aquin': (18.2833, -73.4000),
    'port-salut': (18.0667, -73.9167),
    'camp-perrin': (18.3167, -73.8167),
    'saint-louis-du-sud': (18.2667, -73.5500),
    # Centre
    'hinche': (19.1444, -72.0089),
    'mirebalais': (18.8333, -72.1000),
    'lascahobas': (18.8333, -71.9333),
    'maïssade': (19.1667, -72.1333),
    # Nord-Est
    'fort-liberté': (19.6644, -71.8411),
    'fort-liberte': (19.6644, -71.8411),
    'ouanaminthe': (19.5492, -71.7239),
    'trou-du-nord': (19.6167, -72.0167),
    'terrier-rouge': (19.6333, -71.9333),
    # Nord-Ouest
    'port-de-paix': (19.9389, -72.8292),
    'saint-louis-du-nord': (19.9333, -72.7167),
    'jean-rabel': (19.8500, -73.1833),
    'môle-saint-nicolas': (19.8000, -73.3667),
    # Sud-Est
    'jacmel': (18.2344, -72.5350),
    'marigot': (18.2333, -72.3167),
    'bainet': (18.1833, -72.7500),
    'belle-anse': (18.2333, -72.0667),
    # Grand'Anse
    'jérémie': (18.6436, -74.1167),
    'jeremie': (18.6436, -74.1167),
    "anse-d'hainault": (18.5000, -74.4500),
    'pestel': (18.5500, -73.7833),
    'corail': (18.5667, -73.8833),
    # Nippes
    'miragoâne': (18.4422, -73.0878),
    'miragoane': (18.4422, -73.0878),
    'petite-rivière-de-nippes': (18.4667, -73.2333),
    'anse-à-veau': (18.5000, -73.3500),
    'baradères': (18.4833, -73.6333),
    # Départements (replis)
    'ouest': (18.5392, -72.3364),
    'nord': (19.7595, -72.2042),
    'artibonite': (19.4475, -72.6883),
    'sud': (18.1950, -73.7467),
    'centre': (19.1444, -72.0089),
    'nord-est': (19.6644, -71.8411),
    'nord-ouest': (19.9389, -72.8292),
    'sud-est': (18.2344, -72.5350),
    "grand'anse": (18.6436, -74.1167),
    'nippes': (18.4422, -73.0878),
}

def business_detail(request, business_id=None, pk=None):
    b_id = business_id if business_id is not None else pk
    business = get_object_or_404(Business, pk=b_id)
    
    # Increment view count
    Business.objects.filter(pk=b_id).update(view_count=(business.view_count or 0) + 1)
    business.refresh_from_db(fields=['view_count'])
    
    reviews = business.reviews.all().order_by('-created_at')
    gallery_images = business.images.all()
    similar_businesses = Business.objects.filter(category=business.category, is_active=True).exclude(pk=b_id)[:3]
    
    # Clean phone logic
    raw_phone = business.phone
    clean_phone = ""
    formatted_phone = ""
    if raw_phone:
        digits = re.sub(r'\D', '', str(raw_phone))
        if len(digits) == 8:
            clean_phone = '509' + digits
            formatted_phone = f"+509 {digits[:2]} {digits[2:4]} {digits[4:]}"
        elif len(digits) == 11 and digits.startswith('509'):
            clean_phone = digits
            formatted_phone = f"+509 {digits[3:5]} {digits[5:7]} {digits[7:]}"
        else:
            clean_phone = digits
            formatted_phone = raw_phone
    else:
        # Fallback to official platform support
        clean_phone = "50940746284"
        formatted_phone = "+509 40 74 6284"
        
    msg = f"Bonjou {business.name}, mwen jwenn biznis ou sou EsyConnect Haïti e mwen ta renmen gen plis enfòmasyon."
    encoded_msg = urllib.parse.quote(msg)
    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
    
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, business=business).exists()

    # Résolution des coordonnées GPS et géolocalisation
    has_gps = bool(business.latitude is not None and business.longitude is not None)
    if has_gps:
        lat_clean = f"{business.latitude:.6f}"
        lng_clean = f"{business.longitude:.6f}"
        approx_lat_clean = lat_clean
        approx_lng_clean = lng_clean
    else:
        lat_clean = None
        lng_clean = None
        city_key = str(business.ville_obj.name).strip().lower() if business.ville_obj else ""
        dept_key = str(business.departement_obj.name).strip().lower() if business.departement_obj else ""
        coords = HAITI_COORDINATES.get(city_key) or HAITI_COORDINATES.get(dept_key) or (18.5392, -72.3364)
        approx_lat_clean = f"{coords[0]:.6f}"
        approx_lng_clean = f"{coords[1]:.6f}"

    # Construction de l'adresse textuelle complète
    addr_parts = []
    if business.address:
        addr_parts.append(str(business.address).strip())
    if business.quartier_obj and business.quartier_obj.name:
        addr_parts.append(business.quartier_obj.name)
    if business.ville_obj and business.ville_obj.name:
        addr_parts.append(business.ville_obj.name)
    if business.departement_obj and business.departement_obj.name:
        addr_parts.append(business.departement_obj.name)
    addr_parts.append("Haïti")
    full_address = ", ".join(addr_parts) if addr_parts else "Haïti"

    # Requêtes pour Google Maps (Recherche et Itinéraire)
    query_parts = []
    if business.name:
        query_parts.append(str(business.name).strip())
    if business.address:
        query_parts.append(str(business.address).strip())
    if business.ville_obj and business.ville_obj.name:
        query_parts.append(business.ville_obj.name)
    if business.departement_obj and business.departement_obj.name:
        query_parts.append(business.departement_obj.name)
    query_parts.append("Haiti")
    maps_query = "+".join([urllib.parse.quote_plus(p) for p in query_parts if p])
    maps_search_url = f"https://www.google.com/maps/search/?api=1&query={maps_query}"

    context = {
        'business': business,
        'reviews': reviews,
        'gallery_images': gallery_images,
        'clean_phone': clean_phone,
        'formatted_phone': formatted_phone,
        'whatsapp_url': whatsapp_url,
        'similar_businesses': similar_businesses,
        'is_favorited': is_favorited,
        'has_gps': has_gps,
        'lat_clean': lat_clean,
        'lng_clean': lng_clean,
        'approx_lat_clean': approx_lat_clean,
        'approx_lng_clean': approx_lng_clean,
        'full_address': full_address,
        'maps_search_url': maps_search_url,
    }
    return render(request, 'business/detail.html', context)

def detail(request, business_id=None, pk=None):
    return business_detail(request, business_id=business_id, pk=pk)

@login_required
def business_dashboard(request):
    return render(request, 'business/dashboard.html')

def export_businesses_csv(request):
    """Export all businesses as a CSV file.

    Only staff or superusers can download the CSV for security reasons.
    """
    if not request.user.is_staff:
        return HttpResponse(status=403)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="businesses.csv"'
    writer = csv.writer(response)
    # Header
    writer.writerow([
        'ID', 'Name', 'Category', 'Department', 'Ville', 'Quartier',
        'Address', 'Phone', 'Email', 'Website', 'Created At'
    ])
    for b in Business.objects.select_related('category', 'departement_obj', 'ville_obj', 'quartier_obj'):
        writer.writerow([
            b.id,
            b.name,
            b.category.name if b.category else '',
            b.departement_obj.name if b.departement_obj else '',
            b.ville_obj.name if b.ville_obj else '',
            b.quartier_obj.name if b.quartier_obj else '',
            b.address or '',
            b.phone or '',
            b.email or '',
            b.website or '',
            b.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    return response

@login_required
def toggle_favorite(request, business_id=None, pk=None):
    b_id = business_id if business_id is not None else pk
    business = get_object_or_404(Business, id=b_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        business=business
    )
    if not created:
        favorite.delete()
        return JsonResponse({'success': True, 'is_favorited': False})
    return JsonResponse({'success': True, 'is_favorited': True})

@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('business')
    context = {'favorites': favorites}
    return render(request, 'business/favorites.html', context)

def load_villes(request):
    """Return JSON list of cities for a given department id or name."""
    dept_val = (request.GET.get('department_id') or request.GET.get('departement_id') or request.GET.get('department') or request.GET.get('departement', '')).strip()
    if not dept_val:
        villes = Ville.objects.all().order_by('name').values('id', 'name')
        return JsonResponse(list(villes), safe=False)
    
    if dept_val.isdigit():
        villes = Ville.objects.filter(department_id=int(dept_val)).order_by('name').values('id', 'name')
    else:
        villes = Ville.objects.filter(department__name__icontains=dept_val).order_by('name').values('id', 'name')
    return JsonResponse(list(villes), safe=False)

def load_quartiers(request):
    """Return JSON list of quartiers/zones for a given ville id or name."""
    ville_val = (request.GET.get('ville_id') or request.GET.get('ville') or request.GET.get('city', '')).strip()
    if not ville_val:
        return JsonResponse([], safe=False)
    
    if ville_val.isdigit():
        quartiers = Quartier.objects.filter(ville_id=int(ville_val)).order_by('id').values('id', 'name')
    else:
        from django.utils.text import slugify
        clean_slug = slugify(ville_val)
        matched_ville = Ville.objects.filter(Q(name__icontains=ville_val) | Q(id__in=[v.id for v in Ville.objects.all() if slugify(v.name) == clean_slug])).first()
        if matched_ville:
            quartiers = Quartier.objects.filter(ville=matched_ville).order_by('id').values('id', 'name')
        else:
            quartiers = Quartier.objects.filter(ville__name__icontains=ville_val).order_by('id').values('id', 'name')
    return JsonResponse(list(quartiers), safe=False)

@login_required
def edit_business(request, business_id=None, pk=None):
    b_id = business_id if business_id is not None else pk
    business = get_object_or_404(Business, id=b_id, owner=request.user)
    if request.method == 'POST':
        post_data = request.POST.copy()
        category_val = post_data.get('category')
        custom_category_name = post_data.get('custom_category', '').strip()
        
        custom_cat_obj = None
        if category_val == 'autre' and custom_category_name:
            custom_cat_obj = Category.objects.filter(name__iexact=custom_category_name).first()
            if not custom_cat_obj:
                custom_cat_obj = Category.objects.create(name=custom_category_name, icon="fas fa-store")
            post_data['category'] = str(custom_cat_obj.id)
        elif category_val == 'autre':
            post_data['category'] = ''

        form = BusinessRegistrationForm(post_data, request.FILES, instance=business)
        if form.is_valid():
            b = form.save(commit=False)
            if custom_cat_obj:
                b.category = custom_cat_obj
            b.save()
            messages.success(request, _("Modifications enregistrées avec succès !"))
            return redirect('business:business_detail', business_id=business.id)
        else:
            messages.error(request, _("Veuillez vérifier les informations du formulaire."))
    else:
        form = BusinessRegistrationForm(instance=business)

    categories = Category.objects.all()
    departments = Department.objects.all()
    villes = Ville.objects.filter(department=business.departement_obj) if business.departement_obj else Ville.objects.all()
    context = {
        'form': form,
        'business': business,
        'categories': categories,
        'departments': departments,
        'villes': villes,
        'is_edit': True,
    }
    return render(request, 'business/register_business.html', context)

@login_required
def edit(request, business_id=None, pk=None):
    return edit_business(request, business_id=business_id, pk=pk)

@login_required
def delete_business(request, business_id=None, pk=None):
    b_id = business_id if business_id is not None else pk
    business = get_object_or_404(Business, id=b_id, owner=request.user)
    if request.method == 'POST':
        business.delete()
        return redirect('users:business_dashboard')
    return render(request, 'business/confirm_delete.html', {'business': business})

@login_required
def delete(request, business_id=None, pk=None):
    return delete_business(request, business_id=business_id, pk=pk)

@login_required
def manage_gallery(request, business_id=None, pk=None):
    b_id = business_id if business_id is not None else pk
    business = get_object_or_404(Business, id=b_id, owner=request.user)
    from .models import BusinessGallery

    if request.method == 'POST':
        files = request.FILES.getlist('images') or request.FILES.getlist('image')
        if files:
            count = 0
            for f in files:
                if f.size <= 10 * 1024 * 1024:
                    BusinessGallery.objects.create(business=business, image=f)
                    count += 1
            if count > 0:
                messages.success(request, _(f"{count} photo(s) ajoutée(s) à la galerie avec succès !"))
            else:
                messages.error(request, _("Les photos sélectionnées sont trop volumineuses (maximum 10 Mo par photo)."))
            return redirect('business:manage_gallery', business_id=b_id)
        else:
            messages.error(request, _("Veuillez sélectionner au moins une photo."))

    images = BusinessGallery.objects.filter(business=business).order_by('-created_at')
    context = {
        'business': business,
        'images': images,
        'gallery_images': images,
    }
    return render(request, 'business/manage_gallery.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    businesses = Business.objects.filter(category=category, is_active=True).select_related(
        'category', 'departement_obj', 'ville_obj', 'quartier_obj'
    ).order_by('-is_pro', '-created_at')
    context = {'category': category, 'businesses': businesses}
    return render(request, 'business/category.html', context)

def category(request, category_id):
    return category_detail(request, category_id)

@login_required
def delete_gallery_image(request, business_id=None, image_id=None, pk=None):
    b_id = business_id if business_id is not None else pk
    from .models import BusinessGallery
    business = get_object_or_404(Business, id=b_id, owner=request.user)
    image = get_object_or_404(BusinessGallery, id=image_id, business=business)
    if request.method == 'POST':
        image.delete()
        messages.success(request, _("Photo supprimée avec succès."))
        return redirect('business:manage_gallery', business_id=b_id)
    return redirect('business:manage_gallery', business_id=b_id)

@login_required
def review(request, business_id=None, pk=None):
    b_id = business_id if business_id is not None else pk
    business = get_object_or_404(Business, pk=b_id, is_active=True)
    if request.method == 'POST':
        from .forms import ReviewForm
        # Support both 'comment' and 'review_text'
        post_data = request.POST.copy()
        if 'review_text' in post_data and not post_data.get('comment'):
            post_data['comment'] = post_data.get('review_text')
        form = ReviewForm(post_data)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.business = business
            rev.user = request.user
            rev.save()
            messages.success(request, _("Merci ! Votre avis a été publié avec succès."))
        else:
            messages.error(request, _("Erreur dans le formulaire. Veuillez choisir une note (1-5 étoiles)."))
    return redirect('business:business_detail', business_id=b_id)

def track_click(request, business_id, action_type):
    """AJAX endpoint to record clicks (whatsapp, call) and update metrics."""
    business = get_object_or_404(Business, pk=business_id)
    if action_type == 'whatsapp':
        Business.objects.filter(pk=business_id).update(whatsapp_clicks=(business.whatsapp_clicks or 0) + 1)
        business.refresh_from_db(fields=['whatsapp_clicks'])
    elif action_type == 'call':
        Business.objects.filter(pk=business_id).update(call_count=(business.call_count or 0) + 1)
        business.refresh_from_db(fields=['call_count'])
    
    try:
        from .models import LeadTracking
        LeadTracking.objects.create(business=business, action_type=action_type)
    except Exception:
        pass
    
    return JsonResponse({
        'success': True,
        'action': action_type,
        'whatsapp_clicks': business.whatsapp_clicks,
        'call_count': business.call_count
    })

def departments(request):
    depts = Department.objects.prefetch_related('villes').all()
    return render(request, 'business/departments.html', {'departments': depts})

def ville_detail(request, slug):
    from django.utils.text import slugify
    all_villes = Ville.objects.select_related('department').all()
    ville = None
    for v in all_villes:
        if slugify(v.name) == slug or v.name.lower() == slug.lower():
            ville = v
            break
    if not ville:
        ville = get_object_or_404(Ville, pk=slug) if slug.isdigit() else get_object_or_404(Ville, name__iexact=slug)

    businesses = Business.objects.filter(ville_obj=ville, is_active=True).select_related(
        'category', 'departement_obj', 'ville_obj', 'quartier_obj'
    ).order_by('-is_pro', '-created_at')
    context = {
        'ville': ville,
        'businesses': businesses,
        'business_count': businesses.count(),
    }
    return render(request, 'business/ville_detail.html', context)

def department_detail(request, slug):
    from django.utils.text import slugify
    all_depts = Department.objects.prefetch_related('villes').all()
    dept = None
    for d in all_depts:
        if slugify(d.name) == slug or d.name.lower() == slug.lower():
            dept = d
            break
    if not dept:
        dept = get_object_or_404(Department, pk=slug) if slug.isdigit() else get_object_or_404(Department, name__iexact=slug)

    businesses = Business.objects.filter(departement_obj=dept, is_active=True).select_related(
        'category', 'departement_obj', 'ville_obj', 'quartier_obj'
    ).order_by('-is_pro', '-created_at')
    villes = dept.villes.all()
    context = {
        'department': dept,
        'villes': villes,
        'businesses': businesses,
        'business_count': businesses.count(),
    }
    return render(request, 'business/department_detail.html', context)


def pricing_plans(request):
    """Paj piblik pou prezante tout plan abònman yo."""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order', 'price')
    user_sub = None
    if request.user.is_authenticated:
        user_sub = Subscription.objects.filter(user=request.user, status='active').first()

    context = {
        'plans': plans,
        'user_sub': user_sub,
    }
    return render(request, 'business/pricing.html', context)


@login_required
def checkout_subscription(request, plan_code):
    """Paj pou kòmande oswa soumèt peman pou yon plan (MonCash, Natcash, elatriye)."""
    plan = get_object_or_404(SubscriptionPlan, code=plan_code, is_active=True)

    # Si se plan gratis la
    if plan.price == 0 or plan.code == 'free':
        # Dezaktive nenpòt lòt abònman anvan
        Subscription.objects.filter(user=request.user, status='active').update(status='canceled')
        sub = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='active'
        )
        sub.activate()
        messages.success(request, _("Votre plan Basic gratuit a été activé avec succès !"))
        return redirect('users:subscription_dashboard')

    user_businesses = Business.objects.filter(owner=request.user)

    if request.method == 'POST':
        form = PaymentSubmissionForm(request.POST, request.FILES)
        selected_business_id = request.POST.get('business_id')
        target_business = user_businesses.filter(id=selected_business_id).first() if selected_business_id else None

        if form.is_valid():
            # Kreye abònman nan estati pending
            sub = Subscription.objects.create(
                user=request.user,
                plan=plan,
                business=target_business,
                status='pending'
            )
            transaction = form.save(commit=False)
            transaction.subscription = sub
            transaction.user = request.user
            transaction.business = target_business
            transaction.amount = plan.price
            transaction.currency = plan.currency
            transaction.status = 'pending'
            transaction.save()

            messages.success(
                request,
                _("Merci ! Votre paiement a été soumis avec succès. L'administrateur vérifiera la preuve et activera votre compte PRO rapidement.")
            )
            return redirect('users:subscription_dashboard')
        else:
            messages.error(request, _("Veuillez vérifier les informations saisies."))
    else:
        form = PaymentSubmissionForm()

    context = {
        'plan': plan,
        'form': form,
        'user_businesses': user_businesses,
    }
    return render(request, 'business/checkout_subscription.html', context)


def submit_donation(request):
    """Trete donasyon ak sipò kominotè pou antreprenè Ayisyen yo."""
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if not donation.donor_name or not donation.donor_name.strip():
                donation.donor_name = "Donateur Anonyme"
            donation.status = 'completed'
            donation.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == '1':
                return JsonResponse({
                    'success': True,
                    'message': _("Merci beaucoup pour votre générosité et votre soutien aux petites entreprises haïtiennes !")
                })

            messages.success(request, _("Merci beaucoup pour votre don ! Il a été enregistré avec succès."))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == '1':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.as_json()
                }, status=400)
            messages.error(request, _("Veuillez vérifier le montant et les informations que vous avez saisis."))

    return redirect('business:home')

