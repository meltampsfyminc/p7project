from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Vehicle
from properties.models import District, Local

@login_required
def vehicle_list(request):
    """Display list of vehicles with filtering"""
    vehicles = Vehicle.objects.select_related('local', 'local__district').all()
    
    # Search query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Create separate querysets for each search field
        search_results = Vehicle.objects.none()
        search_results = search_results | vehicles.filter(item_name__icontains=search_query)
        search_results = search_results | vehicles.filter(brand__icontains=search_query)
        search_results = search_results | vehicles.filter(plate_number__icontains=search_query)
        search_results = search_results | vehicles.filter(local__name__icontains=search_query)
        search_results = search_results | vehicles.filter(local__district__name__icontains=search_query)
        search_results = search_results | vehicles.filter(lcode__icontains=search_query)
        search_results = search_results | vehicles.filter(dcode__icontains=search_query)
        vehicles = search_results.distinct()
    
    # Filter by district
    district_filter = request.GET.get('district', '').strip()
    if district_filter:
        district_results = vehicles.filter(local__district__dcode__iexact=district_filter)
        if not district_results.exists():
            district_results = vehicles.filter(local__district__name__icontains=district_filter)
        district_results = district_results | vehicles.filter(dcode__iexact=district_filter)
        vehicles = district_results.distinct()
        
    # Filter by local
    local_filter = request.GET.get('local', '').strip()
    if local_filter:
        local_results = vehicles.filter(local__lcode__iexact=local_filter)
        if not local_results.exists():
            local_results = vehicles.filter(local__name__icontains=local_filter)
        local_results = local_results | vehicles.filter(lcode__iexact=local_filter)
        vehicles = local_results.distinct()
        
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
        'vehicles': vehicles,
        'districts': districts,
        'locals': locals_list,
        'search_query': search_query,
        'current_district': district_filter,
        'current_district_name': current_district_obj.name if current_district_obj else '',
        'current_local': local_filter,
        'current_local_name': current_local_obj.name if current_local_obj else '',
    }
    return render(request, 'vehicles/vehicle_list.html', context)
