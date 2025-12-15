# national/management/commands/copy_previous_year.py
from django.core.management.base import BaseCommand
from django.db import transaction
from national.models import Report, PastoralHouse, OfficeBuilding, OtherBuilding, Chapel

class Command(BaseCommand):
    help = 'Copy building data from previous year to new year report'
    
    def add_arguments(self, parser):
        parser.add_argument('local_code', type=str, help='Local code (lcode)')
        parser.add_argument('year', type=int, help='Target year for new report')
    
    def handle(self, *args, **options):
        local_code = options['local_code']
        target_year = options['year']
        
        from national.models import Local
        try:
            local = Local.objects.get(lcode=local_code)
        except Local.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Local with code {local_code} not found'))
            return
        
        # Check if target report already exists
        if Report.objects.filter(local=local, year=target_year).exists():
            self.stdout.write(self.style.WARNING(
                f'Report for {local_code} year {target_year} already exists'
            ))
            return
        
        # Get previous year report
        prev_report = Report.objects.filter(
            local=local, 
            year=target_year-1
        ).first()
        
        if not prev_report:
            self.stdout.write(self.style.WARNING(
                f'No previous year report found for {local_code} year {target_year-1}'
            ))
            return
        
        with transaction.atomic():
            # Create new report
            new_report = Report.objects.create(
                local=local,
                year=target_year,
                filename=f'auto_generated_{target_year}',
                uploaded_by=prev_report.uploaded_by
            )
            
            # Copy Pastoral Houses
            for ph in prev_report.pastoral_houses.all():
                PastoralHouse.objects.create(
                    report=new_report,
                    description=ph.description,
                    house_class=ph.house_class,
                    date_built=ph.date_built,
                    old_cost=ph.total_cost,  # Copy the calculated total
                    add_this_year=0,
                    sub_this_year=0
                )
            
            # Copy Office Buildings
            for office in prev_report.offices.all():
                OfficeBuilding.objects.create(
                    report=new_report,
                    office_name=office.office_name,
                    office_class=office.office_class,
                    date_built=office.date_built,
                    old_cost=office.total_cost,
                    add_this_year=0,
                    sub_this_year=0
                )
            
            # Copy Other Buildings
            for building in prev_report.other_buildings.all():
                OtherBuilding.objects.create(
                    report=new_report,
                    building_name=building.building_name,
                    building_class=building.building_class,
                    date_built=building.date_built,
                    old_cost=building.total_cost,
                    add_this_year=0,
                    sub_this_year=0
                )
            
            # Copy Chapels
            for chapel in prev_report.chapels.all():
                Chapel.objects.create(
                    report=new_report,
                    year=target_year,
                    dcode=chapel.dcode,
                    lcode=chapel.lcode,
                    lokal=chapel.lokal,
                    chapel_class=chapel.chapel_class,
                    seating_capacity=chapel.seating_capacity,
                    offered=chapel.offered,
                    date_offered=chapel.date_offered,
                    date_built=chapel.date_built,
                    funded_by=chapel.funded_by,
                    original_cost=chapel.original_cost,
                    last_year_cost=chapel.total_cost_this_year,  # Copy the calculated total
                    add_construction=0,
                    add_renovation=0,
                    add_general_repair=0,
                    add_others=0,
                    total_added=0,
                    deduction_amount=0,
                    deduction_reason='',
                    remarks='Copied from previous year'
                )
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {target_year} report for {local_code} with {new_report.pastoral_houses.count()} pastoral houses, '
                f'{new_report.offices.count()} offices, {new_report.other_buildings.count()} other buildings, '
                f'and {new_report.chapels.count()} chapels'
            ))