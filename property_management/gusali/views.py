from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.management import call_command
from io import StringIO
import os

from .models import Building, BuildingYearlyRecord
from properties.models import District, Local


@login_required
def building_list(request):
    """Display list of all buildings with filtering by district, local, code, and year"""
    buildings = Building.objects.select_related('local', 'local__district').all()
    
    # Search query (searches district code, district name, local code, local name)
    search_query = request.GET.get('q', '').strip()
    if search_query:
        buildings = buildings.filter(
            Q(local__lcode__icontains=search_query) |
            Q(local__name__icontains=search_query) |
            Q(local__district__dcode__icontains=search_query) |
            Q(local__district__name__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    
    # Filter by district code or name
    district_filter = request.GET.get('district', '').strip()
    if district_filter:
        buildings = buildings.filter(
            Q(local__district__dcode__iexact=district_filter) |
            Q(local__district__name__icontains=district_filter)
        )
    
    # Filter by local code or name
    local_filter = request.GET.get('local', '').strip()
    if local_filter:
        buildings = buildings.filter(
            Q(local__lcode__iexact=local_filter) |
            Q(local__name__icontains=local_filter)
        )
    
    # Filter by building code
    code_filter = request.GET.get('code')
    if code_filter:
        buildings = buildings.filter(code=code_filter)
    
    # Filter by year
    year_filter = request.GET.get('year')
    if year_filter:
        buildings = buildings.filter(year_covered=year_filter)
    
    # Calculate totals
    total_cost = buildings.aggregate(total=Sum('current_total_cost'))['total'] or 0
    
    # Get unique years for filter dropdown
    years = Building.objects.values_list('year_covered', flat=True).distinct().order_by('-year_covered')
    
    # Get districts and locals for filter dropdowns
    districts = District.objects.all().order_by('name')
    locals_list = Local.objects.select_related('district').all().order_by('district__name', 'name')
    
    context = {
        'buildings': buildings,
        'total_cost': total_cost,
        'years': years,
        'districts': districts,
        'locals': locals_list,
        'search_query': search_query,
        'current_district': district_filter,
        'current_local': local_filter,
        'current_code': code_filter,
        'current_year': year_filter,
        'code_choices': Building.BUILDING_CODE_CHOICES,
    }
    return render(request, 'gusali/building_list.html', context)



@login_required
def building_detail(request, pk):
    """Display building details with yearly records"""
    building = get_object_or_404(Building, pk=pk)
    yearly_records = building.yearly_records.all().order_by('-year')
    
    context = {
        'building': building,
        'yearly_records': yearly_records,
    }
    return render(request, 'gusali/building_detail.html', context)


@login_required
def building_upload(request):
    """Handle GUSALI REPORT file upload"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Validate file extension
        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Please upload an Excel file (.xlsx or .xls)')
            return redirect('gusali:building_upload')
        
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
            call_command('import_gusali', file_path, stdout=out)
            messages.success(request, f'Successfully imported: {uploaded_file.name}')
            messages.info(request, out.getvalue())
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
        
        return redirect('gusali:building_list')
    
    # Get recent imports
    from properties.models import ImportedFile
    recent_imports = ImportedFile.objects.filter(
        filename__icontains='GUSALI'
    ).order_by('-imported_at')[:10]
    
    context = {
        'recent_imports': recent_imports,
    }
    return render(request, 'gusali/building_upload.html', context)


@login_required
def building_report(request):
    """Display building summary report"""
    buildings = Building.objects.all()
    
    # Group by code
    code_summary = {}
    for code, label in Building.BUILDING_CODE_CHOICES:
        code_buildings = buildings.filter(code=code)
        code_summary[code] = {
            'label': label,
            'count': code_buildings.count(),
            'total_cost': code_buildings.aggregate(total=Sum('current_total_cost'))['total'] or 0,
        }
    
    # Overall totals
    total_buildings = buildings.count()
    total_cost = buildings.aggregate(total=Sum('current_total_cost'))['total'] or 0
    
    # Yearly totals
    yearly_records = BuildingYearlyRecord.objects.values('year').annotate(
        total_added=Sum('total_added'),
        total_removed=Sum('broken_removed_cost'),
        year_end_total=Sum('year_end_total'),
    ).order_by('-year')
    
    context = {
        'code_summary': code_summary,
        'total_buildings': total_buildings,
        'total_cost': total_cost,
        'yearly_records': yearly_records,
    }
    return render(request, 'gusali/building_report.html', context)
