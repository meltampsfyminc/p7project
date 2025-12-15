from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
from django.http import HttpResponse
from django.forms import modelformset_factory
from django.db import transaction
import tempfile, os
from datetime import datetime

from .models import (
    District, Local, Report,
    Chapel, PastoralHouse, OfficeBuilding, OtherBuilding,
    Item, ItemsSummary,
    ItemAdded, ItemAddedSummary,
    ItemRemoved, ItemRemovedSummary,
    Land, LandSummary,
    Plant, PlantSummary,
    Vehicle, VehicleSummary,
    ReportSummary, Page1Summary
)

from .forms import ReportForm, PastoralHouseForm, OfficeBuildingForm, OtherBuildingForm, ChapelForm
from national.management.commands.utils_export import render_to_pdf, render_to_docx

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_previous_year_report(local, year):
    """Get the previous year's report for a local"""
    try:
        return Report.objects.get(local=local, year=year-1)
    except Report.DoesNotExist:
        return None

def copy_building_data(source_report, target_report):
    """Copy all building data from one report to another"""
    with transaction.atomic():
        # Copy Pastoral Houses
        for ph in source_report.pastoral_houses.all():
            ph.pk = None  # Create new instance
            ph.report = target_report
            ph.old_cost = ph.total_cost  # Use current total as old cost for new year
            ph.add_this_year = 0
            ph.sub_this_year = 0
            ph.save()
        
        # Copy Office Buildings
        for office in source_report.offices.all():
            office.pk = None
            office.report = target_report
            office.old_cost = office.total_cost
            office.add_this_year = 0
            office.sub_this_year = 0
            office.save()
        
        # Copy Other Buildings
        for building in source_report.other_buildings.all():
            building.pk = None
            building.report = target_report
            building.old_cost = building.total_cost
            building.add_this_year = 0
            building.sub_this_year = 0
            building.save()
        
        # Copy Chapels
        for chapel in source_report.chapels.all():
            chapel.pk = None
            chapel.report = target_report
            chapel.last_year_cost = chapel.total_cost_this_year
            chapel.add_construction = 0
            chapel.add_renovation = 0
            chapel.add_general_repair = 0
            chapel.add_others = 0
            chapel.total_added = 0
            chapel.deduction_amount = 0
            chapel.deduction_reason = ''
            chapel.save()
    
    return target_report

# ============================================================================
# EXISTING VIEWS (KEEP THESE AS THEY ARE)
# ============================================================================

@login_required
def district_list(request):
    districts = District.objects.all().order_by("dcode")
    return render(request, "national/district_list.html", {"districts": districts})

@login_required
def local_list(request, dcode):
    district = get_object_or_404(District, dcode=dcode)
    locals = district.locals.all().order_by("lcode")
    return render(request, "national/local_list.html", {"district": district, "locals": locals})

@login_required
def report_list(request, local_id):
    local = get_object_or_404(Local, id=local_id)
    reports = local.reports.all().order_by("-year")
    return render(request, "national/report_list.html", {"local": local, "reports": reports})

def report_print_pdf(request, report_id):
    """Generate PDF or DOCX output for a complete National report."""
    report = get_object_or_404(Report, id=report_id)
    local = report.local
    district = local.district

    # Build context
    context = {
        "report": report,
        "local": local,
        "district": district,
        "chapels": report.chapels.all(),
        "pastoral": report.pastoral_houses.all(),
        "offices": report.offices.all(),
        "other_buildings": report.other_buildings.all(),
        "items": report.items.all(),
        "added_items": report.items_added.all(),
        "removed_items": report.items_removed.all(),
        "lands": report.lands.all(),
        "plants": report.plants.all(),
        "vehicles": report.vehicles.all(),
    }
    
    # Add summaries with try-except
    summary_fields = [
        'page1_summary', 'items_summary', 'items_added_summary',
        'items_removed_summary', 'land_summary', 'plant_summary',
        'vehicle_summary', 'summary'
    ]
    
    for field in summary_fields:
        try:
            context[field] = getattr(report, field)
        except:
            context[field] = None

    fmt = request.GET.get("format", "pdf").lower()

    if fmt == "docx":
        docx_bytes = render_to_docx(context)
        filename = f"Report-{district.dcode}-{local.lcode}-{report.year}.docx"
        response = HttpResponse(
            docx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    pdf_bytes = render_to_pdf("national/report_print.html", context)
    if not pdf_bytes:
        return HttpResponse("Failed to generate PDF.", status=500)

    filename = f"Report-{district.dcode}-{local.lcode}-{report.year}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Build context with try-except for OneToOne relationships
    context = {
        "report": report,
        "chapels": report.chapels.all(),
        "pastoral_houses": report.pastoral_houses.all(),
        "offices": report.offices.all(),
        "other_buildings": report.other_buildings.all(),
        "items": report.items.all(),
        "items_added": report.items_added.all(),
        "items_removed": report.items_removed.all(),
        "lands": report.lands.all(),
        "plants": report.plants.all(),
        "vehicles": report.vehicles.all(),
    }
    
    # Add summaries
    summary_fields = [
        ('page1_summary', Page1Summary),
        ('items_summary', ItemsSummary),
        ('items_added_summary', ItemAddedSummary),
        ('items_removed_summary', ItemRemovedSummary),
        ('land_summary', LandSummary),
        ('plant_summary', PlantSummary),
        ('vehicle_summary', VehicleSummary),
        ('summary', ReportSummary)
    ]
    
    for field_name, model in summary_fields:
        try:
            context[field_name] = getattr(report, field_name)
        except model.DoesNotExist:
            context[field_name] = None

    return render(request, "national/report_detail.html", context)

def district_summary(request, dcode):
    district = get_object_or_404(District, dcode=dcode)
    locals = district.locals.all()
    reports = Report.objects.filter(local__in=locals)

    context = {
        "district": district,
        "locals": locals,
        "reports": reports,
    }
    return render(request, "national/district_summary.html", context)

@login_required
def upload_file(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "No file selected")
            return redirect("national:upload")

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        for chunk in file.chunks():
            temp.write(chunk)
        temp.close()

        try:
            call_command("import_national", file=temp.name, user=request.user.id)
            messages.success(request, "File imported successfully.")
        except Exception as e:
            messages.error(request, f"Import failed: {e}")
        finally:
            os.unlink(temp.name)

        return redirect("national:district_list")

    return render(request, "national/upload.html")

# ============================================================================
# NEW VIEWS FOR YEAR-OVER-YEAR TRACKING
# ============================================================================

@login_required
def create_report(request, local_id):
    """Create a new report, optionally copy from previous year"""
    local = get_object_or_404(Local, id=local_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.local = local
            report.uploaded_by = request.user
            
            # Check if report already exists for this year
            if Report.objects.filter(local=local, year=report.year).exists():
                messages.error(request, f'A report already exists for year {report.year}.')
                return render(request, 'national/report_create.html', {'form': form, 'local': local})
            
            report.save()
            
            # Check if user wants to copy from previous year
            copy_from = request.POST.get('copy_from_previous')
            if copy_from == 'yes':
                prev_report = get_previous_year_report(local, report.year)
                if prev_report:
                    copy_building_data(prev_report, report)
                    messages.success(request, f'Report created and data copied from {prev_report.year}.')
                else:
                    messages.success(request, 'Report created. No previous year data to copy.')
            else:
                messages.success(request, f'Report for {report.year} created successfully.')
            
            return redirect('national:report_detail', report_id=report.id)
    else:
        # Pre-fill year as next year from latest report
        latest_report = local.reports.order_by('-year').first()
        initial_year = latest_report.year + 1 if latest_report else datetime.now().year
        
        form = ReportForm(initial={
            'year': initial_year,
            'filename': f'report_{initial_year}'
        })
    
    # Check if there's a previous year to copy from
    latest_report = local.reports.order_by('-year').first()
    has_previous = latest_report is not None
    
    context = {
        'form': form,
        'local': local,
        'has_previous': has_previous,
        'latest_year': latest_report.year if latest_report else None,
    }
    return render(request, 'national/report_create.html', context)

@login_required
def copy_report(request, report_id):
    """Create a copy of a report for the next year"""
    source_report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        new_year = int(request.POST.get('new_year', source_report.year + 1))
        
        # Check if report already exists for that year
        if Report.objects.filter(local=source_report.local, year=new_year).exists():
            messages.error(request, f'A report already exists for year {new_year}.')
            return redirect('national:report_detail', report_id=source_report.id)
        
        # Create new report
        new_report = Report.objects.create(
            local=source_report.local,
            year=new_year,
            filename=f'report_{new_year}',
            uploaded_by=request.user
        )
        
        # Copy all building data
        copy_building_data(source_report, new_report)
        
        messages.success(request, 
            f'Report copied to {new_year}. '
            f'Copied: {new_report.pastoral_houses.count()} pastoral houses, '
            f'{new_report.offices.count()} offices, '
            f'{new_report.other_buildings.count()} other buildings, '
            f'{new_report.chapels.count()} chapels.')
        return redirect('national:report_detail', report_id=new_report.id)
    
    # Suggest next year
    next_year = source_report.year + 1
    
    context = {
        'source_report': source_report,
        'next_year': next_year,
    }
    return render(request, 'national/copy_report.html', context)

@login_required
def add_pastoral_house(request, report_id):
    """Add pastoral house with auto-fill from previous year"""
    report = get_object_or_404(Report, id=report_id)
    
    # Get previous year's report for this local
    prev_report = get_previous_year_report(report.local, report.year)
    
    if request.method == 'POST':
        form = PastoralHouseForm(request.POST)
        if form.is_valid():
            pastoral_house = form.save(commit=False)
            pastoral_house.report = report
            
            # If old_cost not provided, try to auto-fill from previous year
            if not pastoral_house.old_cost and prev_report:
                # Look for building with similar description
                prev_house = prev_report.pastoral_houses.filter(
                    description__icontains=pastoral_house.description
                ).first()
                if prev_house:
                    pastoral_house.old_cost = prev_house.total_cost
            
            pastoral_house.save()
            messages.success(request, 'Pastoral house added successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        # Pre-fill with previous year's data if building_id is provided
        building_id = request.GET.get('building_id')
        initial_data = {}
        
        if building_id and prev_report:
            try:
                prev_house = prev_report.pastoral_houses.get(id=building_id)
                initial_data = {
                    'description': prev_house.description,
                    'house_class': prev_house.house_class,
                    'date_built': prev_house.date_built,
                    'old_cost': prev_house.total_cost,
                }
            except PastoralHouse.DoesNotExist:
                pass
        
        form = PastoralHouseForm(initial=initial_data)
    
    # Get previous year's buildings for quick selection
    prev_buildings = prev_report.pastoral_houses.all() if prev_report else []
    
    context = {
        'form': form,
        'report': report,
        'prev_buildings': prev_buildings,
        'has_prev_year': bool(prev_report),
    }
    return render(request, 'national/add_pastoral_house.html', context)

@login_required
def edit_pastoral_house(request, report_id, building_id):
    """Edit an existing pastoral house"""
    report = get_object_or_404(Report, id=report_id)
    pastoral_house = get_object_or_404(PastoralHouse, id=building_id, report=report)
    
    if request.method == 'POST':
        form = PastoralHouseForm(request.POST, instance=pastoral_house)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pastoral house updated successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        form = PastoralHouseForm(instance=pastoral_house)
    
    context = {
        'form': form,
        'report': report,
        'pastoral_house': pastoral_house,
    }
    return render(request, 'national/edit_pastoral_house.html', context)

@login_required
def add_office_building(request, report_id):
    """Add office building with auto-fill from previous year"""
    report = get_object_or_404(Report, id=report_id)
    prev_report = get_previous_year_report(report.local, report.year)
    
    if request.method == 'POST':
        form = OfficeBuildingForm(request.POST)
        if form.is_valid():
            office = form.save(commit=False)
            office.report = report
            
            # Auto-fill old_cost from previous year
            if not office.old_cost and prev_report:
                prev_office = prev_report.offices.filter(
                    office_name__icontains=office.office_name
                ).first()
                if prev_office:
                    office.old_cost = prev_office.total_cost
            
            office.save()
            messages.success(request, 'Office building added successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        building_id = request.GET.get('building_id')
        initial_data = {}
        
        if building_id and prev_report:
            try:
                prev_office = prev_report.offices.get(id=building_id)
                initial_data = {
                    'office_name': prev_office.office_name,
                    'office_class': prev_office.office_class,
                    'date_built': prev_office.date_built,
                    'old_cost': prev_office.total_cost,
                }
            except OfficeBuilding.DoesNotExist:
                pass
        
        form = OfficeBuildingForm(initial=initial_data)
    
    prev_buildings = prev_report.offices.all() if prev_report else []
    
    context = {
        'form': form,
        'report': report,
        'prev_buildings': prev_buildings,
        'has_prev_year': bool(prev_report),
    }
    return render(request, 'national/add_office_building.html', context)

@login_required
def edit_office_building(request, report_id, building_id):
    """Edit an existing office building"""
    report = get_object_or_404(Report, id=report_id)
    office = get_object_or_404(OfficeBuilding, id=building_id, report=report)
    
    if request.method == 'POST':
        form = OfficeBuildingForm(request.POST, instance=office)
        if form.is_valid():
            form.save()
            messages.success(request, 'Office building updated successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        form = OfficeBuildingForm(instance=office)
    
    context = {
        'form': form,
        'report': report,
        'office': office,
    }
    return render(request, 'national/edit_office_building.html', context)

@login_required
def add_other_building(request, report_id):
    """Add other building with auto-fill from previous year"""
    report = get_object_or_404(Report, id=report_id)
    prev_report = get_previous_year_report(report.local, report.year)
    
    if request.method == 'POST':
        form = OtherBuildingForm(request.POST)
        if form.is_valid():
            building = form.save(commit=False)
            building.report = report
            
            # Auto-fill old_cost from previous year
            if not building.old_cost and prev_report:
                prev_building = prev_report.other_buildings.filter(
                    building_name__icontains=building.building_name
                ).first()
                if prev_building:
                    building.old_cost = prev_building.total_cost
            
            building.save()
            messages.success(request, 'Building added successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        building_id = request.GET.get('building_id')
        initial_data = {}
        
        if building_id and prev_report:
            try:
                prev_building = prev_report.other_buildings.get(id=building_id)
                initial_data = {
                    'building_name': prev_building.building_name,
                    'building_class': prev_building.building_class,
                    'date_built': prev_building.date_built,
                    'old_cost': prev_building.total_cost,
                }
            except OtherBuilding.DoesNotExist:
                pass
        
        form = OtherBuildingForm(initial=initial_data)
    
    prev_buildings = prev_report.other_buildings.all() if prev_report else []
    
    context = {
        'form': form,
        'report': report,
        'prev_buildings': prev_buildings,
        'has_prev_year': bool(prev_report),
    }
    return render(request, 'national/add_other_building.html', context)

@login_required
def edit_other_building(request, report_id, building_id):
    """Edit an existing other building"""
    report = get_object_or_404(Report, id=report_id)
    building = get_object_or_404(OtherBuilding, id=building_id, report=report)
    
    if request.method == 'POST':
        form = OtherBuildingForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            messages.success(request, 'Building updated successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        form = OtherBuildingForm(instance=building)
    
    context = {
        'form': form,
        'report': report,
        'building': building,
    }
    return render(request, 'national/edit_other_building.html', context)

@login_required
def add_chapel(request, report_id):
    """Add chapel with auto-fill from previous year"""
    report = get_object_or_404(Report, id=report_id)
    prev_report = get_previous_year_report(report.local, report.year)
    
    if request.method == 'POST':
        form = ChapelForm(request.POST)
        if form.is_valid():
            chapel = form.save(commit=False)
            chapel.report = report
            
            # Auto-fill last_year_cost from previous year
            if not chapel.last_year_cost and prev_report:
                prev_chapel = prev_report.chapels.filter(
                    lokal=chapel.lokal,
                    chapel_class=chapel.chapel_class
                ).first()
                if prev_chapel:
                    chapel.last_year_cost = prev_chapel.total_cost_this_year
            
            chapel.save()
            messages.success(request, 'Chapel added successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        chapel_id = request.GET.get('chapel_id')
        initial_data = {}
        
        if chapel_id and prev_report:
            try:
                prev_chapel = prev_report.chapels.get(id=chapel_id)
                initial_data = {
                    'lokal': prev_chapel.lokal,
                    'chapel_class': prev_chapel.chapel_class,
                    'seating_capacity': prev_chapel.seating_capacity,
                    'date_built': prev_chapel.date_built,
                    'last_year_cost': prev_chapel.total_cost_this_year,
                }
            except Chapel.DoesNotExist:
                pass
        
        form = ChapelForm(initial=initial_data)
    
    prev_chapels = prev_report.chapels.all() if prev_report else []
    
    context = {
        'form': form,
        'report': report,
        'prev_chapels': prev_chapels,
        'has_prev_year': bool(prev_report),
    }
    return render(request, 'national/add_chapel.html', context)

@login_required
def edit_chapel(request, report_id, chapel_id):
    """Edit an existing chapel"""
    report = get_object_or_404(Report, id=report_id)
    chapel = get_object_or_404(Chapel, id=chapel_id, report=report)
    
    if request.method == 'POST':
        form = ChapelForm(request.POST, instance=chapel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chapel updated successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        form = ChapelForm(instance=chapel)
    
    context = {
        'form': form,
        'report': report,
        'chapel': chapel,
    }
    return render(request, 'national/edit_chapel.html', context)

@login_required
def bulk_add_buildings(request, report_id):
    """Add multiple buildings at once with copy from previous year"""
    report = get_object_or_404(Report, id=report_id)
    prev_report = get_previous_year_report(report.local, report.year)
    
    PastoralHouseFormSet = modelformset_factory(
        PastoralHouse, 
        form=PastoralHouseForm, 
        extra=5,
        fields=['description', 'house_class', 'date_built', 'old_cost', 'add_this_year', 'sub_this_year']
    )
    
    if request.method == 'POST':
        formset = PastoralHouseFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            saved_count = 0
            for instance in instances:
                if instance.description:  # Only save if there's data
                    instance.report = report
                    
                    # Auto-fill old_cost from previous year
                    if not instance.old_cost and prev_report:
                        prev_house = prev_report.pastoral_houses.filter(
                            description__icontains=instance.description
                        ).first()
                        if prev_house:
                            instance.old_cost = prev_house.total_cost
                    
                    instance.save()
                    saved_count += 1
            
            messages.success(request, f'{saved_count} buildings added successfully.')
            return redirect('national:report_detail', report_id=report.id)
    else:
        # Pre-populate with previous year's buildings if requested
        copy_all = request.GET.get('copy_all') == 'true'
        if copy_all and prev_report:
            initial_data = []
            for prev_house in prev_report.pastoral_houses.all():
                initial_data.append({
                    'description': prev_house.description,
                    'house_class': prev_house.house_class,
                    'date_built': prev_house.date_built,
                    'old_cost': prev_house.total_cost,
                    'add_this_year': 0,
                    'sub_this_year': 0,
                })
            formset = PastoralHouseFormSet(queryset=PastoralHouse.objects.none(), 
                                         initial=initial_data)
        else:
            formset = PastoralHouseFormSet(queryset=PastoralHouse.objects.none())
    
    context = {
        'formset': formset,
        'report': report,
        'has_prev_year': bool(prev_report),
        'prev_buildings_count': prev_report.pastoral_houses.count() if prev_report else 0,
    }
    return render(request, 'national/bulk_add_buildings.html', context)

@login_required
def copy_buildings_from_previous(request, report_id):
    """Copy all buildings from previous year to current report"""
    report = get_object_or_404(Report, id=report_id)
    prev_report = get_previous_year_report(report.local, report.year)
    
    if not prev_report:
        messages.error(request, 'No previous year report found to copy from.')
        return redirect('national:report_detail', report_id=report_id)
    
    # Check if current report already has buildings
    has_existing = (
        report.pastoral_houses.exists() or 
        report.offices.exists() or 
        report.other_buildings.exists() or
        report.chapels.exists()
    )
    
    if request.method == 'POST':
        # Copy buildings
        copy_building_data(prev_report, report)
        
        messages.success(request, 
            f'Successfully copied buildings from {prev_report.year} to {report.year}. '
            f'Copied: {report.pastoral_houses.count()} pastoral houses, '
            f'{report.offices.count()} offices, '
            f'{report.other_buildings.count()} other buildings, '
            f'{report.chapels.count()} chapels.')
        return redirect('national:report_detail', report_id=report.id)
    
    context = {
        'report': report,
        'prev_report': prev_report,
        'has_existing': has_existing,
        'pastoral_count': prev_report.pastoral_houses.count(),
        'office_count': prev_report.offices.count(),
        'other_count': prev_report.other_buildings.count(),
        'chapel_count': prev_report.chapels.count(),
    }
    return render(request, 'national/copy_buildings.html', context)