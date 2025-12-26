from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.core.management import call_command
from io import StringIO
import os

from .models import LocalEquipment
from properties.models import District, Local


@login_required
def equipment_list(request):
    """Display list of all equipment with filtering"""
    equipment = LocalEquipment.objects.select_related('local', 'local__district').all()
    
    # Search query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        equipment = equipment.filter(
            Q(item_name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(local__lcode__icontains=search_query) |
            Q(local__name__icontains=search_query) |
            Q(local__district__dcode__icontains=search_query) |
            Q(local__district__name__icontains=search_query)
        )
    
    # Filter by district
    district_filter = request.GET.get('district', '').strip()
    if district_filter:
        equipment = equipment.filter(
            Q(local__district__dcode__iexact=district_filter) |
            Q(local__district__name__icontains=district_filter)
        )
    
    # Filter by local
    local_filter = request.GET.get('local', '').strip()
    if local_filter:
        equipment = equipment.filter(
            Q(local__lcode__iexact=local_filter) |
            Q(local__name__icontains=local_filter)
        )
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter:
        equipment = equipment.filter(location=location_filter)
    
    # Filter by year reported
    year_filter = request.GET.get('year')
    if year_filter:
        equipment = equipment.filter(year_reported=year_filter)
    
    # Filter by new additions only
    new_only = request.GET.get('new_only')
    if new_only:
        equipment = equipment.filter(is_new_addition=True)
    
    # Calculate totals
    total_value = equipment.aggregate(total=Sum('total_price'))['total'] or 0
    total_items = equipment.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Get filter options
    years = LocalEquipment.objects.values_list('year_reported', flat=True).distinct().order_by('-year_reported')
    districts = District.objects.all().order_by('name')
    locals_list = Local.objects.select_related('district').all().order_by('district__name', 'name')
    
    context = {
        'equipment': equipment,
        'total_value': total_value,
        'total_items': total_items,
        'years': years,
        'districts': districts,
        'locals': locals_list,
        'location_choices': LocalEquipment.LOCATION_CHOICES,
        'search_query': search_query,
        'current_district': district_filter,
        'current_local': local_filter,
        'current_location': location_filter,
        'current_year': year_filter,
        'new_only': new_only,
    }
    return render(request, 'kagamitan/equipment_list.html', context)


@login_required
def equipment_detail(request, pk):
    """Display equipment item details"""
    item = get_object_or_404(LocalEquipment, pk=pk)
    
    # Get other items at same local
    related_items = LocalEquipment.objects.filter(
        local=item.local
    ).exclude(pk=pk).order_by('location', 'item_name')[:10]
    
    context = {
        'item': item,
        'related_items': related_items,
    }
    return render(request, 'kagamitan/equipment_detail.html', context)


@login_required
def equipment_upload(request):
    """Handle equipment report file upload"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Validate file extension
        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Please upload an Excel file (.xlsx or .xls)')
            return redirect('kagamitan:equipment_upload')
        
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
        
        return redirect('kagamitan:equipment_list')
    
    # Get recent imports
    from properties.models import ImportedFile
    recent_imports = ImportedFile.objects.filter(
        filename__icontains='Page'
    ).order_by('-imported_at')[:10]
    
    context = {
        'recent_imports': recent_imports,
    }
    return render(request, 'kagamitan/equipment_upload.html', context)


@login_required
def equipment_report(request):
    """Display equipment summary report"""
    equipment = LocalEquipment.objects.all()
    
    # Summary by location
    location_summary = {}
    for location_code, location_label in LocalEquipment.LOCATION_CHOICES:
        loc_items = equipment.filter(location=location_code)
        location_summary[location_code] = {
            'label': location_label,
            'count': loc_items.aggregate(total=Sum('quantity'))['total'] or 0,
            'total_value': loc_items.aggregate(total=Sum('total_price'))['total'] or 0,
        }
    
    # Overall totals
    total_items = equipment.aggregate(total=Sum('quantity'))['total'] or 0
    total_value = equipment.aggregate(total=Sum('total_price'))['total'] or 0
    new_items = equipment.filter(is_new_addition=True).aggregate(total=Sum('quantity'))['total'] or 0
    
    # By year
    yearly_summary = equipment.values('year_reported').annotate(
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
    return render(request, 'kagamitan/equipment_report.html', context)
