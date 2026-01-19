from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from admin_core.models import (
    Department,
    Section,
    Worker,
    HousingSite,
    HousingBuilding,
    HousingUnit,
    HousingUnitAssignment,
    SyncRun,
    SyncConflict,
)

from properties.models import HousingUnit as SrcHousingUnit


# ======================================================
# MAIN ENTRY POINT
# ======================================================

@transaction.atomic
def run_admin_core_sync(
    *,
    source="properties_sync",
    triggered_by="system"
) -> SyncRun:
    """
    Synchronizes housing + worker data from properties app
    into admin_core (normalized domain).

    NEVER auto-resolves conflicts.
    """

    start_time = timezone.now()

    sync_run = SyncRun.objects.create(
        source=source,
        triggered_by=triggered_by,
        status="success",
        started_at=start_time,
    )

    counters = {
        "departments_created": 0,
        "sections_created": 0,
        "workers_created": 0,
        "buildings_created": 0,
        "assignments_created": 0,
        "conflicts": 0,
    }

    # ==================================================
    # 1. READ SOURCE DATA (properties)
    # ==================================================

    source_units = (
        SrcHousingUnit.objects
        .select_related("pamayanan", "building")
        .all()
    )

    for src in source_units:

        # ----------------------------------------------
        # A. HOUSING SITE (Pamayanan)
        # ----------------------------------------------

        site_name = src.pamayanan.name.strip()

        site, site_created = HousingSite.objects.get_or_create(
            name=site_name,
            defaults={
                "address": src.address or "",
                "is_multi_building": bool(src.building),
            }
        )

        # ----------------------------------------------
        # B. HOUSING BUILDING (optional)
        # ----------------------------------------------

        building = None
        if src.building:
            building, b_created = HousingBuilding.objects.get_or_create(
                site=site,
                name=src.building.name.strip()
            )
            if b_created:
                counters["buildings_created"] += 1

        # ----------------------------------------------
        # C. HOUSING UNIT
        # ----------------------------------------------

        unit_label = src.housing_unit_name.strip()

        unit, _ = HousingUnit.objects.get_or_create(
            site=site,
            building=building,
            unit_label=unit_label,
            defaults={
                "floor": str(src.floor or "").strip(),
            }
        )

        # ----------------------------------------------
        # D. WORKER (from occupant_name)
        # ----------------------------------------------

        if not src.occupant_name:
            continue

        names = src.occupant_name.strip().split()
        if len(names) < 2:
            continue

        first_name = names[0]
        last_name = names[-1]
        middle_name = " ".join(names[1:-1]) if len(names) > 2 else ""

        identity_hash = Worker(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            category="MWA"
        ).generate_identity_hash()

        worker = Worker.objects.filter(identity_hash=identity_hash).first()

        if not worker:
            worker = Worker.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                category="MWA",
                employment_status="active",
            )
            counters["workers_created"] += 1

        # ----------------------------------------------
        # E. DEPARTMENT / SECTION (CONFLICT-AWARE)
        # ----------------------------------------------

        if src.department:
            dept, d_created = Department.objects.get_or_create(
                name=src.department.strip()
            )
            if d_created:
                counters["departments_created"] += 1

            if src.section:
                Section.objects.get_or_create(
                    department=dept,
                    name=src.section.strip()
                )

        # ----------------------------------------------
        # F. HOUSING ASSIGNMENT (CONFLICT CHECK)
        # ----------------------------------------------

        current_assignment = HousingUnitAssignment.objects.filter(
            worker=worker,
            is_current=True
        ).first()

        if current_assignment:
            if current_assignment.housing_unit != unit:
                SyncConflict.objects.create(
                    conflict_type="HOUSING_ASSIGNMENT",
                    severity="medium",
                    worker=worker,
                    identity_hash=worker.identity_hash,
                    existing_value=str(current_assignment.housing_unit),
                    incoming_value=str(unit),
                    source=source,
                )
                counters["conflicts"] += 1
                sync_run.status = "partial"
        else:
            HousingUnitAssignment.objects.create(
                worker=worker,
                housing_unit=unit,
                is_current=True,
            )
            counters["assignments_created"] += 1

    # ==================================================
    # FINALIZE SYNC RUN
    # ==================================================

    sync_run.finished_at = timezone.now()
    sync_run.duration_ms = int(
        (sync_run.finished_at - sync_run.started_at).total_seconds() * 1000
    )

    sync_run.departments_created = counters["departments_created"]
    sync_run.sections_created = counters["sections_created"]
    sync_run.workers_created = counters["workers_created"]
    sync_run.buildings_created = counters["buildings_created"]
    sync_run.assignments_created = counters["assignments_created"]
    sync_run.conflicts_detected = counters["conflicts"]

    if counters["conflicts"] > 0:
        sync_run.status = "partial"

    sync_run.save()

    return sync_run
