from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Plant
from .forms import PlantForm
from properties.models import District, Local

@login_required
def plant_list(request):
    """Display list of plants with filtering"""
    plants = Plant.objects.select_related('local', 'local__district').all()
    
    # Search query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Create separate querysets for each search field
        search_results = Plant.objects.none()
        search_results = search_results | plants.filter(local__name__icontains=search_query)
        search_results = search_results | plants.filter(local__district__name__icontains=search_query)
        search_results = search_results | plants.filter(name__icontains=search_query)
        search_results = search_results | plants.filter(variety__icontains=search_query)
        search_results = search_results | plants.filter(lcode__icontains=search_query)
        search_results = search_results | plants.filter(dcode__icontains=search_query)
        plants = search_results.distinct()
    
    # Filter by district
    district_filter = request.GET.get('district', '').strip()
    if district_filter:
        district_results = plants.filter(local__district__dcode__iexact=district_filter)
        if not district_results.exists():
            district_results = plants.filter(local__district__name__icontains=district_filter)
        district_results = district_results | plants.filter(dcode__iexact=district_filter)
        plants = district_results.distinct()
    
    # Filter by local
    local_filter = request.GET.get('local', '').strip()
    if local_filter:
        local_results = plants.filter(local__lcode__iexact=local_filter)
        if not local_results.exists():
            local_results = plants.filter(local__name__icontains=local_filter)
        local_results = local_results | plants.filter(lcode__iexact=local_filter)
        plants = local_results.distinct()
        
    # Get filter options
    districts = District.objects.all().order_by('name')
    locals_list = Local.objects.select_related('district').all().order_by('district__name', 'name')
    
    # Filter locals by district if selected (for dependent dropdown)
    current_district_obj = None
    if district_filter:
        current_district_obj = District.objects.filter(dcode=district_filter).first()
        locals_list = locals_list.filter(district__dcode=district_filter)
        
    current_local_obj = None
    if local_filter:
        current_local_obj = Local.objects.filter(lcode=local_filter).first()
        
    context = {
        'plants': plants,
        'districts': districts,
        'locals': locals_list,
        'search_query': search_query,
        'current_district': district_filter,
        'current_district_name': current_district_obj.name if current_district_obj else '',
        'current_local': local_filter,
        'current_local_name': current_local_obj.name if current_local_obj else '',
    }
    return render(request, 'plants/plant_list.html', context)

@login_required
def plant_detail(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    return render(request, 'plants/plant_detail.html', {'plant': plant})

@login_required
def plant_create(request):
    if request.method == 'POST':
        form = PlantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant created successfully.')
            return redirect('plants:plant_list')
    else:
        form = PlantForm()
    return render(request, 'plants/plant_form.html', {'form': form, 'title': 'Create Plant'})

@login_required
def plant_update(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    if request.method == 'POST':
        form = PlantForm(request.POST, instance=plant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant updated successfully.')
            return redirect('plants:plant_detail', pk=pk)
    else:
        form = PlantForm(instance=plant)
    return render(request, 'plants/plant_form.html', {'form': form, 'title': 'Update Plant'})

@login_required
def plant_delete(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    if request.method == 'POST':
        plant.delete()
        messages.success(request, 'Plant deleted successfully.')
        return redirect('plants:plant_list')
    return render(request, 'plants/plant_confirm_delete.html', {'plant': plant})

@login_required
def plant_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Logic matches Lupa upload
        return render(request, 'plants/plant_upload.html', {'success': True})
    return render(request, 'plants/plant_upload.html')