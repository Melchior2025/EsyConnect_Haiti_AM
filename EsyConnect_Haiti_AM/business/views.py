import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from .models import Business, Department, Ville, Category, Review, BusinessGallery
from .forms import BusinessRegistrationForm, ReviewForm, BusinessGalleryForm


def home(request):
    # Get active businesses for featured section
    latest_businesses = Business.objects.filter(is_active=True).order_by('-created_at')[:6]
    all_businesses = Business.objects.filter(is_active=True)
    
    # Prepare JSON for Leaflet map (only needed fields)
    businesses_json = json.dumps(list(all_businesses.exclude(latitude__isnull=True).exclude(longitude__isnull=True).values(
        'id', 'name', 'latitude', 'longitude', 'logo', 'category__name', 'is_pro', 'is_verified', 'address'
    )))
    departments = Department.objects.all()
    context = {
        'latest_businesses': latest_businesses,
        'all_businesses': all_businesses,
        'businesses_json': businesses_json,
        'departments': departments,
    }
    return render(request, 'business/home.html', context)


def categories(request):
    cats = Category.objects.all()
    return render(request, 'business/categories.html', {'categories': cats})


def about(request):
    return render(request, 'business/about.html')


def contact_general(request):
    if request.method == 'POST':
        messages.success(request, _("Mèsi pou mesaj ou a ! Nou resevwa l epi n ap reponn ou talè."))
        return redirect('business:contact_general')
    return render(request, 'business/contact.html')


def search(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    departement_id = request.GET.get('departement') or request.GET.get('department')
    ville_id = request.GET.get('ville')

    businesses = Business.objects.filter(is_active=True)
    if query:
        businesses = businesses.filter(name__icontains=query)
    if category_id:
        businesses = businesses.filter(category_id=category_id)
    if departement_id:
        businesses = businesses.filter(departement_obj_id=departement_id)
    if ville_id:
        businesses = businesses.filter(ville_obj_id=ville_id)

    context = {
        'businesses': businesses,
        'query': query,
        'categories': Category.objects.all(),
        'departments': Department.objects.all(),
    }
    return render(request, 'business/search_results.html', context)


def load_villes(request):
    department_id = request.GET.get('department_id') or request.GET.get('departement_id')
    if not department_id:
        return JsonResponse([], safe=False)
    villes = Ville.objects.filter(department_id=department_id).values('id', 'name')
    data = [{'id': v['id'], 'name': v['name'], 'nom': v['name']} for v in villes]
    return JsonResponse(data, safe=False)


def favorites(request):
    favorite_ids = request.session.get('favorites', [])
    businesses = Business.objects.filter(id__in=favorite_ids, is_active=True)
    return render(request, 'business/favorites.html', {'businesses': businesses})


def toggle_favorite(request, business_id):
    business = get_object_or_404(Business, pk=business_id)
    favorites_list = request.session.get('favorites', [])
    if business.id in favorites_list:
        favorites_list.remove(business.id)
        messages.info(request, _("Biznis la retire nan lis favori ou yo."))
    else:
        favorites_list.append(business.id)
        messages.success(request, _("Biznis la ajoute nan lis favori ou yo !"))
    request.session['favorites'] = favorites_list
    request.session.modified = True
    return redirect('business:detail', business_id=business.id)


def detail(request, business_id):
    business = get_object_or_404(Business, pk=business_id, is_active=True)
    # Increment view count safely
    Business.objects.filter(pk=business_id).update(view_count=business.view_count + 1)
    business.refresh_from_db(fields=['view_count'])

    reviews = business.reviews.select_related('user').all()
    review_form = ReviewForm()
    is_favorite = business.id in request.session.get('favorites', [])
    
    context = {
        'business': business,
        'business_id': business.id,
        'reviews': reviews,
        'review_form': review_form,
        'is_favorite': is_favorite,
    }
    return render(request, 'business/detail.html', context)


def category(request, category_id):
    cat = get_object_or_404(Category, pk=category_id)
    businesses = Business.objects.filter(category=cat, is_active=True)
    return render(request, 'business/category.html', {'category': cat, 'businesses': businesses})


@login_required
def register_business(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        category_val = post_data.get('category')
        custom_category_name = post_data.get('custom_category', '').strip()
        
        if category_val == 'autre' and custom_category_name:
            custom_cat_obj, created = Category.objects.get_or_create(name=custom_category_name)
            post_data['category'] = str(custom_cat_obj.id)
        elif category_val == 'autre':
            post_data['category'] = ''

        form = BusinessRegistrationForm(post_data, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            messages.success(request, _("Felisitasyon ! Biznis ou an anrejistre avèk siksè."))
            return redirect('business:detail', business_id=business.id)
        else:
            messages.error(request, _("Tanpri verifye fòmilè a, gen kèk erè ki dwe korije."))
    else:
        form = BusinessRegistrationForm()

    categories = Category.objects.all()
    departments = Department.objects.all()
    context = {
        'form': form,
        'categories': categories,
        'departments': departments,
        'is_edit': False,
    }
    return render(request, 'business/register_business.html', context)


@login_required
def edit(request, business_id):
    business = get_object_or_404(Business, pk=business_id)
    if not (request.user == business.owner or request.user.is_superuser):
        messages.error(request, _("Ou pa gen otorizasyon pou modifye biznis sa a."))
        return redirect('business:detail', business_id=business.id)

    if request.method == 'POST':
        post_data = request.POST.copy()
        category_val = post_data.get('category')
        custom_category_name = post_data.get('custom_category', '').strip()
        
        if category_val == 'autre' and custom_category_name:
            custom_cat_obj, created = Category.objects.get_or_create(name=custom_category_name)
            post_data['category'] = str(custom_cat_obj.id)
        elif category_val == 'autre':
            post_data['category'] = ''

        form = BusinessRegistrationForm(post_data, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, _("Modifikasyon yo anrejistre avèk siksè !"))
            return redirect('business:detail', business_id=business.id)
        else:
            messages.error(request, _("Tanpri verifye fòmilè a, gen kèk erè ki dwe korije."))
    else:
        form = BusinessRegistrationForm(instance=business)

    categories = Category.objects.all()
    departments = Department.objects.all()
    villes = Ville.objects.filter(department=business.departement_obj) if business.departement_obj else Ville.objects.none()

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
def manage_gallery(request, business_id):
    business = get_object_or_404(Business, pk=business_id)
    if not (request.user == business.owner or request.user.is_superuser):
        messages.error(request, _("Ou pa gen otorizasyon pou jere galri sa a."))
        return redirect('business:detail', business_id=business.id)

    if request.method == 'POST':
        form = BusinessGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_img = form.save(commit=False)
            gallery_img.business = business
            gallery_img.save()
            messages.success(request, _("Foto a ajoute nan galri a avèk siksè !"))
            return redirect('business:manage_gallery', business_id=business.id)
        else:
            messages.error(request, _("Erè pandan telechajman imaj la."))
    else:
        form = BusinessGalleryForm()

    gallery_images = business.images.all()
    context = {
        'business': business,
        'form': form,
        'gallery_images': gallery_images,
    }
    return render(request, 'business/manage_gallery.html', context)


@login_required
def delete(request, business_id):
    business = get_object_or_404(Business, pk=business_id)
    if not (request.user == business.owner or request.user.is_superuser):
        messages.error(request, _("Ou pa gen otorizasyon pou efase biznis sa a."))
        return redirect('business:detail', business_id=business.id)

    if request.method == 'POST':
        name = business.name
        business.delete()
        messages.success(request, _(f"Biznis '{name}' la efase avèk siksè."))
        return redirect('users:business_dashboard')
    return redirect('business:detail', business_id=business.id)


@login_required
def delete_gallery_image(request, business_id, image_id):
    business = get_object_or_404(Business, pk=business_id)
    if not (request.user == business.owner or request.user.is_superuser):
        messages.error(request, _("Ou pa gen otorizasyon."))
        return redirect('business:detail', business_id=business.id)

    img = get_object_or_404(business.images, pk=image_id)
    img.delete()
    messages.success(request, _("Foto a efase nan galri a."))
    return redirect('business:manage_gallery', business_id=business.id)


@login_required
def review(request, business_id):
    business = get_object_or_404(Business, pk=business_id, is_active=True)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.business = business
            rev.user = request.user
            rev.save()
            messages.success(request, _("Mèsi ! Avi ou a anrejistre avèk siksè."))
        else:
            messages.error(request, _("Erè nan fòmilè avi a. Tanpri verifye nòt ak kòmantè a."))
    return redirect('business:detail', business_id=business.id)


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

    businesses = Business.objects.filter(ville_obj=ville, is_active=True)
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

    businesses = Business.objects.filter(departement_obj=dept, is_active=True)
    villes = dept.villes.all()
    context = {
        'department': dept,
        'villes': villes,
        'businesses': businesses,
        'business_count': businesses.count(),
    }
    return render(request, 'business/department_detail.html', context)