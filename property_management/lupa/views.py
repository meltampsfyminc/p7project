from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Land
from properties.models import District, Local

@login_required
def land_list(request):
    """Display list of lands with filtering"""
    lands = Land.objects.select_related('local', 'local__district').all()
    
    # Search query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Create separate querysets for each search field
        search_results = Land.objects.none()
        
        # Search in local name
        search_results = search_results | lands.filter(local__name__icontains=search_query)
        
        # Search in district name
        search_results = search_results | lands.filter(local__district__name__icontains=search_query)
        
        # Search in location
        search_results = search_results | lands.filter(location__icontains=search_query)
        
        # Search in owner
        search_results = search_results | lands.filter(owner__icontains=search_query)
        
        # Search in status
        search_results = search_results | lands.filter(status__icontains=search_query)
        
        # Search in lcode
        search_results = search_results | lands.filter(lcode__icontains=search_query)
        
        # Search in dcode
        search_results = search_results | lands.filter(dcode__icontains=search_query)
        
        lands = search_results.distinct()
    
    # Filter by district
    district_filter = request.GET.get('district', '').strip()
    if district_filter:
        # Try filtering by exact district code first
        district_results = lands.filter(local__district__dcode__iexact=district_filter)
        
        # If no results, try by district name
        if not district_results.exists():
            district_results = lands.filter(local__district__name__icontains=district_filter)
        
        # Also check land's own dcode
        district_results = district_results | lands.filter(dcode__iexact=district_filter)
        
        lands = district_results.distinct()
    
    # Filter by local
    local_filter = request.GET.get('local', '').strip()
    if local_filter:
        # Try filtering by exact local code first
        local_results = lands.filter(local__lcode__iexact=local_filter)
        
        # If no results, try by local name
        if not local_results.exists():
            local_results = lands.filter(local__name__icontains=local_filter)
        
        # Also check land's own lcode
        local_results = local_results | lands.filter(lcode__iexact=local_filter)
        
        lands = local_results.distinct()

        
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
        'lands': lands,
        'districts': districts,
        'locals': locals_list,
        'search_query': search_query,
        'current_district': district_filter,
        'current_district_name': current_district_obj.name if current_district_obj else '',
        'current_local': local_filter,
        'current_local_name': current_local_obj.name if current_local_obj else '',
    }
    return render(request, 'lupa/land_list.html', context)

@login_required
def land_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Save file logic (simplified for now, ideally use ImportedFile model)
        # Call management command
        return render(request, 'lupa/land_upload.html', {'success': True})
    return render(request, 'lupa/land_upload.html')
