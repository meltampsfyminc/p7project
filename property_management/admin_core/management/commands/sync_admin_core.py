from django.db import transaction
from django.utils import timezone

from properties.models import (
    Pamayanan,
    HousingUnit as SourceHousingUnit,
)

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


def run_sync(triggered_by="properties_import"):
    """
    Canonical admin_core sync service.
    Safe to call from:
    - signals
    - views / API
    - celery
    """

    start_time = timezone.now()

    sync_run = SyncRun.objects.create(
        source="properties_sync",
        triggered_by=triggered_by,
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

            # =====================================================
            # 1. SYNC HOUSING SITES & BUILDINGS
            # =====================================================
            pamayanans = Pamayanan.objects.prefetch_related("buildings")

            for pam in pamayanans:
                site, site_created = HousingSite.objects.get_or_create(
                    name=pam.name,
                    defaults={
                        "address": pam.address,
                        "is_multi_building": pam.buildings.exists(),
                    },
                )
                if site_created:
                    counters["housing_sites"] += 1

                for b in pam.buildings.all():
                    building, b_created = HousingBuilding.objects.get_or_create(
                        site=site,
                        name=b.name,
                    )
                    if b_created:
                        counters["housing_buildings"] += 1

            # =====================================================
            # 2. SYNC HOUSING UNITS + WORKERS
            # =====================================================
            source_units = SourceHousingUnit.objects.select_related(
                "pamayanan", "building"
            )

            for src in source_units:
                site = HousingSite.objects.get(name=src.pamayanan.name)

                building = None
                if src.building:
                    building = HousingBuilding.objects.get(
                        site=site,
                        name=src.building.name,
                    )

                unit_label = src.housing_unit_name or src.unit_number

                unit, unit_created = HousingUnit.objects.get_or_create(
                    site=site,
                    building=building,
                    unit_label=unit_label,
                    defaults={"floor": src.floor or ""},
                )
                if unit_created:
                    counters["housing_units"] += 1

                # ------------------------------
                # Worker Extraction
                # ------------------------------
                if not src.occupant_name:
                    continue

                parts = src.occupant_name.strip().split()
                if len(parts) < 2:
                    continue

                first_name = parts[0]
                last_name = parts[-1]
                middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""

                temp_worker = Worker(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    category="MWA",
                )
                identity_hash = temp_worker.generate_identity_hash()

                worker = Worker.objects.filter(identity_hash=identity_hash).first()
                if not worker:
                    temp_worker.identity_hash = identity_hash
                    temp_worker.save()
                    worker = temp_worker
                    counters["workers"] += 1

                # ------------------------------
                # Department & Section
                # ------------------------------
                department = None
                if src.department:
                    department, _ = Department.objects.get_or_create(
                        name=src.department.strip()
                    )

                if src.section and department:
                    Section.objects.get_or_create(
                        department=department,
                        name=src.section.strip(),
                    )

                # ------------------------------
                # Housing Assignment
                # ------------------------------
                assignment, created = HousingUnitAssignment.objects.get_or_create(
                    worker=worker,
                    housing_unit=unit,
                    is_current=True,
                    defaults={
                        "start_date": src.date_reported or timezone.now().date()
                    },
                )
                if created:
                    counters["assignments"] += 1

    except Exception as e:
        sync_run.status = "failed"
        sync_run.notes = str(e)
        raise

    # =====================================================
    # FINALIZE SYNC RUN
    # =====================================================
    sync_run.finished_at = timezone.now()
    sync_run.duration_ms = int(
        (sync_run.finished_at - start_time).total_seconds() * 1000
    )
    sync_run.conflicts_detected = counters["conflicts"]
    sync_run.notes = f"Synced: {counters}"
    sync_run.save()

    return sync_run
