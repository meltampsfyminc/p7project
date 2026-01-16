from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from properties.models import Pamayanan, PamayananBuilding, HousingUnit as SourceHousingUnit
from admin_core.models import (
    HousingSite,
    HousingBuilding,
    HousingUnit,
    Worker,
    HousingUnitAssignment,
    Department,
    Section,
    SyncRun,
    SyncConflict,
)


class Command(BaseCommand):
    help = "Sync housing and occupants data from properties into admin_core"

    def handle(self, *args, **options):
        start_time = timezone.now()
        sync_run = SyncRun.objects.create(
            source="properties_sync",
            started_at=start_time,
            status="success",
        )

        counters = {
            "housing_sites": 0,
            "housing_buildings": 0,
            "housing_units": 0,
            "workers": 0,
            "assignments": 0,
            "conflicts": 0,
        }

        try:
            with transaction.atomic():
                self.stdout.write("🔄 Syncing Housing Sites...")

                pamayanans = Pamayanan.objects.all()

                for pam in pamayanans:
                    site, created = HousingSite.objects.get_or_create(
                        name=pam.name,
                        defaults={
                            "address": pam.address,
                            "is_multi_building": pam.buildings.exists(),
                        },
                    )
                    if created:
                        counters["housing_sites"] += 1

                    # Buildings (if any)
                    for b in pam.buildings.all():
                        building, b_created = HousingBuilding.objects.get_or_create(
                            site=site,
                            name=b.name,
                        )
                        if b_created:
                            counters["housing_buildings"] += 1

                self.stdout.write("🏠 Syncing Housing Units...")

                for src_unit in SourceHousingUnit.objects.select_related(
                    "pamayanan", "building"
                ):
                    site = HousingSite.objects.get(name=src_unit.pamayanan.name)

                    building = None
                    if src_unit.building:
                        building = HousingBuilding.objects.get(
                            site=site,
                            name=src_unit.building.name,
                        )

                    unit_label = src_unit.housing_unit_name or f"Unit {src_unit.unit_number}"

                    unit, created = HousingUnit.objects.get_or_create(
                        site=site,
                        building=building,
                        unit_label=unit_label,
                        defaults={"floor": src_unit.floor or ""},
                    )
                    if created:
                        counters["housing_units"] += 1

                    # -------- Worker --------
                    if not src_unit.occupant_name:
                        continue

                    names = src_unit.occupant_name.strip().split()
                    if len(names) < 2:
                        continue

                    first_name = names[0]
                    last_name = names[-1]
                    middle_name = " ".join(names[1:-1]) if len(names) > 2 else ""

                    worker = Worker(
                        first_name=first_name,
                        middle_name=middle_name,
                        last_name=last_name,
                        category="MWA",
                    )
                    identity_hash = worker.generate_identity_hash()

                    existing = Worker.objects.filter(identity_hash=identity_hash).first()

                    if not existing:
                        worker.identity_hash = identity_hash
                        worker.save()
                        existing = worker
                        counters["workers"] += 1

                    # -------- Department / Section --------
                    department = None
                    if src_unit.department:
                        department, _ = Department.objects.get_or_create(
                            name=src_unit.department.strip()
                        )

                    if src_unit.section and department:
                        Section.objects.get_or_create(
                            department=department,
                            name=src_unit.section.strip(),
                        )

                    # -------- Assignment --------
                    assignment, a_created = HousingUnitAssignment.objects.get_or_create(
                        worker=existing,
                        housing_unit=unit,
                        is_current=True,
                        defaults={
                            "start_date": src_unit.date_reported or timezone.now().date()
                        },
                    )
                    if a_created:
                        counters["assignments"] += 1

        except Exception as e:
            sync_run.status = "failed"
            sync_run.notes = str(e)
            raise

        sync_run.finished_at = timezone.now()
        sync_run.duration_ms = int(
            (sync_run.finished_at - start_time).total_seconds() * 1000
        )
        sync_run.conflicts_detected = counters["conflicts"]
        sync_run.notes = f"Synced {counters}"
        sync_run.save()

        self.stdout.write(self.style.SUCCESS("✅ admin_core sync complete"))
