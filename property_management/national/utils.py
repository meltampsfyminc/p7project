# national/utils.py
from django.db import transaction

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

def auto_fill_old_costs(building_instance):
    """Auto-fill old_cost from previous year if not set"""
    if not building_instance.old_cost:
        prev_report = get_previous_year_report(
            building_instance.report.local,
            building_instance.report.year
        )
        if prev_report:
            # Logic depends on building type
            if hasattr(building_instance, 'description'):  # PastoralHouse
                prev = prev_report.pastoral_houses.filter(
                    description=building_instance.description
                ).first()
            elif hasattr(building_instance, 'office_name'):  # OfficeBuilding
                prev = prev_report.offices.filter(
                    office_name=building_instance.office_name
                ).first()
            elif hasattr(building_instance, 'building_name'):  # OtherBuilding
                prev = prev_report.other_buildings.filter(
                    building_name=building_instance.building_name
                ).first()
            
            if prev:
                return prev.total_cost
    return None