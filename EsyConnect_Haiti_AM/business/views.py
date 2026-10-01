from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import Business, Department
from .models import Ville

def home(request):
    # Get active businesses for featured section
    latest_businesses = Business.objects.filter(is_active=True).order_by('-created_at')[:6]
    all_businesses = Business.objects.filter(is_active=True)
    # Prepare JSON for Leaflet map (only needed fields)
    businesses_json = json.dumps(list(all_businesses.exclude(latitude__isnull=True).exclude(longitude__isnull=True).values(
        'id', 'name', 'latitude', 'longitude', 'logo', 'category__name', 'is_pro', 'is_verified', 'address'
    )))
    # Departments for search dropdown
    departments = Department.objects.all()
    context = {
        'latest_businesses': latest_businesses,
        'all_businesses': all_businesses,
        'businesses_json': businesses_json,
        'departments': departments,
    }
    return render(request, 'business/home.html', context)

def categories(request):
    return render(request, 'business/categories.html')

def about(request):
    return render(request, 'business/about.html')

def contact_general(request):
    return render(request, 'business/contact.html')

def search(request):
    return render(request, 'business/search_results.html')

def load_villes(request):
    department_id = request.GET.get('department_id') or request.GET.get('departement_id')
    if not department_id:
        return JsonResponse([], safe=False)
    villes = Ville.objects.filter(department_id=department_id).values('id', 'name')
    data = [{'id': v['id'], 'name': v['name'], 'nom': v['name']} for v in villes]
    return JsonResponse(data, safe=False)

def favorites(request):
    return render(request, 'business/favorites.html')

def detail(request, business_id):
    from django.shortcuts import get_object_or_404
    business = get_object_or_404(Business, pk=business_id, is_active=True)
    reviews = business.reviews.select_related('user').all()
    context = {'business': business, 'business_id': business.id, 'reviews': reviews}
    return render(request, 'business/detail.html', context)

def category(request, category_id):
    return render(request, 'business/category.html')

def register_business(request):
    if request.method == 'POST':
        return render(request, 'business/register_business.html')
    return render(request, 'business/register_business.html')

def edit(request, business_id):
    return render(request, 'business/register_business.html')

def manage_gallery(request, business_id):
    return render(request, 'business/manage_gallery.html')

def delete(request, business_id):
    from django.shortcuts import redirect
    return redirect('business:home')

def delete_gallery_image(request, business_id, image_id):
    from django.shortcuts import redirect
    return redirect('business:manage_gallery', business_id=business_id)

def toggle_favorite(request, business_id):
    from django.shortcuts import redirect
    return redirect('business:detail', business_id=business_id)

def review(request, business_id):
    from django.shortcuts import redirect
    return redirect('business:detail', business_id=business_id)

def departments(request):
    return render(request, 'business/departments.html')

def ville_detail(request, slug):
    return render(request, 'business/ville_detail.html')

def department_detail(request, slug):
    return render(request, 'business/department_detail.html')