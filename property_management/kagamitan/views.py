from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.management import call_command
from io import StringIO
import os

from .models import Item
from properties.models import District, Local


@login_required
def item_list(request):
    """Display list of items with filtering"""
    items = Item.objects.select_related('local', 'local__district').all()
    
    # Search query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Create separate querysets for each search field
        search_results = Item.objects.none()
        
        # Search in item name
        search_results = search_results | items.filter(item_name__icontains=search_query)
        
        # Search in brand
        search_results = search_results | items.filter(brand__icontains=search_query)
        
        # Search in local lcode
        search_results = search_results | items.filter(local__lcode__icontains=search_query)
        
        # Search in item's own lcode
        search_results = search_results | items.filter(lcode__icontains=search_query)
        
        # Search in local name
        search_results = search_results | items.filter(local__name__icontains=search_query)
        
        # Search in district dcode
        search_results = search_results | items.filter(local__district__dcode__icontains=search_query)
        
        # Search in item's own dcode
        search_results = search_results | items.filter(dcode__icontains=search_query)
        
        # Search in district name
        search_results = search_results | items.filter(local__district__name__icontains=search_query)
        
        # Search in property number
        search_results = search_results | items.filter(property_number__icontains=search_query)
        
        items = search_results.distinct()
    
    # Filter by district
    district_filter = request.GET.get('district', '').strip()
    if district_filter:
        # Try filtering by exact district code first
        district_results = items.filter(local__district__dcode__iexact=district_filter)
        
        # If no results, try by district name
        if not district_results.exists():
            district_results = items.filter(local__district__name__icontains=district_filter)
        
        # Also check item's own dcode
        district_results = district_results | items.filter(dcode__iexact=district_filter)
        
        items = district_results.distinct()
    
    # Filter by local
    local_filter = request.GET.get('local', '').strip()
    if local_filter:
        # Try filtering by exact local code first
        local_results = items.filter(local__lcode__iexact=local_filter)
        
        # If no results, try by local name
        if not local_results.exists():
            local_results = items.filter(local__name__icontains=local_filter)
        
        # Also check item's own lcode
        local_results = local_results | items.filter(lcode__iexact=local_filter)
        
        items = local_results.distinct()

    
    # Filter by location
    location_filter = request.GET.get('location', '').strip()
    if location_filter:
        items = items.filter(location=location_filter)
    
    # Filter by year reported
    year_filter = request.GET.get('year')
    if year_filter:
        items = items.filter(year_reported=year_filter)
    
    # Filter by new additions only
    new_only = request.GET.get('new_only')
    if new_only:
        items = items.filter(is_new=True)
    
    # Calculate totals
    total_value = items.aggregate(total=Sum('total_price'))['total'] or 0
    total_items = items.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Get filter options
    years = Item.objects.values_list('year_reported', flat=True).distinct().order_by('-year_reported')
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
        
    locations = Item.objects.values_list('location', flat=True).distinct().order_by('location')
    
    context = {
        'items': items,
        'total_value': total_value,
        'total_items': total_items,
        'years': years,
        'districts': districts,
        'locals': locals_list,
        'locations': locations,
        'search_query': search_query,
        'current_district': district_filter,
        'current_district_name': current_district_obj.name if current_district_obj else '',
        'current_local': local_filter,
        'current_local_name': current_local_obj.name if current_local_obj else '',
        'current_location': location_filter,
        'current_year': year_filter,
        'new_only': new_only,
    }
    return render(request, 'kagamitan/item_list.html', context)


@login_required
def item_detail(request, pk):
    """Display item details"""
    item = get_object_or_404(Item, pk=pk)
    
    # Get other items at same local
    related_items = Item.objects.filter(
        local=item.local
    ).exclude(pk=pk).order_by('location', 'item_name')[:10]
    
    context = {
        'item': item,
        'related_items': related_items,
    }
    return render(request, 'kagamitan/item_detail.html', context)


@login_required
def item_upload(request):
    """Handle item report file upload"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Validate file extension
        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Please upload an Excel file (.xlsx or .xls)')
            return redirect('kagamitan:item_upload')
        
        # Save file temporarily
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded_file.name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Run import command
        try:
            out = StringIO()
            call_command('import_kagamitan', file_path, stdout=out)
            messages.success(request, f'Successfully imported: {uploaded_file.name}')
            messages.info(request, out.getvalue())
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
        
        return redirect('kagamitan:item_list')
    
    # Get recent imports
    from properties.models import ImportedFile
    recent_imports = ImportedFile.objects.filter(
        filename__icontains='Page'
    ).order_by('-imported_at')[:10]
    
    context = {
        'recent_imports': recent_imports,
    }
    return render(request, 'kagamitan/item_upload.html', context)


@login_required
def item_report(request):
    """Display item summary report"""
    items = Item.objects.all()
    
    # Summary by location
    location_summary = {}
    locations = Item.objects.values_list('location', flat=True).distinct().order_by('location')
    
    for loc in locations:
        if not loc: continue
        loc_items = items.filter(location=loc)
        location_summary[loc] = {
            'label': loc,
            'count': loc_items.aggregate(total=Sum('quantity'))['total'] or 0,
            'total_value': loc_items.aggregate(total=Sum('total_price'))['total'] or 0,
        }
    
    # Overall totals
    total_items = items.aggregate(total=Sum('quantity'))['total'] or 0
    total_value = items.aggregate(total=Sum('total_price'))['total'] or 0
    new_items = items.filter(is_new=True).aggregate(total=Sum('quantity'))['total'] or 0
    
    # By year
    yearly_summary = items.values('year_reported').annotate(
        item_count=Sum('quantity'),
        total_value=Sum('total_price'),
    ).order_by('-year_reported')
    
    context = {
        'location_summary': location_summary,
        'total_items': total_items,
        'total_value': total_value,
        'new_items': new_items,
        'yearly_summary': yearly_summary,
    }
    return render(request, 'kagamitan/item_report.html', context)
