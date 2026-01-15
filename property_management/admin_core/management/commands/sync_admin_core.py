from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import json
import time

from admin_core.models import (
    Department,
    Section,
    AdminBuilding,
    Office,
    Worker,
    WorkerOfficeAssignment,
    HousingUnitAssignment,
    SyncConflict,
    SyncRun,
)

from properties.models import HousingUnit


class Command(BaseCommand):
    help = "Sync data from properties app into admin_core with audit log and guardrails"

    def handle(self, *args, **options):
        start_time = time.time()

        self.stdout.write(self.style.SUCCESS("\nStarting Admin Core sync...\n"))

        # --------------------------------------------------
        # AUDIT: Start SyncRun
        # --------------------------------------------------
        sync_run = SyncRun.objects.create(
            source="properties_sync",
            triggered_by="management_command",
            status="success",
            started_at=timezone.now(),
        )

        stats = {
            "departments": 0,
            "sections": 0,
            "workers": 0,
            "buildings": 0,
            "offices": 0,
            "assignments": 0,
            "conflicts": 0,
        }

        try:
            housing_units = (
                HousingUnit.objects
                .select_related("property")
                .exclude(occupant_name__isnull=True)
                .exclude(occupant_name__exact="")
            )

            with transaction.atomic():
                for hu in housing_units:

                    # ==================================================
                    # A. DEPARTMENT
                    # ==================================================
                    department, created = Department.objects.get_or_create(
                        name=hu.department.strip()
                    )
                    if created:
                        stats["departments"] += 1

                    # ==================================================
                    # B. SECTION
                    # ==================================================
                    section, created = Section.objects.get_or_create(
                        department=department,
                        name=hu.section.strip()
                    )
                    if created:
                        stats["sections"] += 1

                    # ==================================================
                    # C. WORKER IDENTITY (preserves middle initials)
                    # ==================================================
                    # NOTE:
                    # Name parsing intentionally preserves middle initials
                    # (e.g. "M.", "T.") and compound names.
                    # Do NOT normalize or strip punctuation.
                    parts = hu.occupant_name.strip().split()

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

                    worker = Worker.objects.filter(
                        identity_hash=identity_hash
                    ).first()

                    if worker:
                        # ------------------------------
                        # Conflict: identity mismatch
                        # ------------------------------
                        if (
                            worker.first_name.lower() != first_name.lower()
                            or worker.last_name.lower() != last_name.lower()
                        ):
                            SyncConflict.objects.create(
                                conflict_type="WORKER_IDENTITY",
                                severity="high",
                                worker=worker,
                                identity_hash=identity_hash,
                                existing_value=json.dumps({
                                    "first_name": worker.first_name,
                                    "middle_name": worker.middle_name,
                                    "last_name": worker.last_name,
                                }),
                                incoming_value=json.dumps({
                                    "first_name": first_name,
                                    "middle_name": middle_name,
                                    "last_name": last_name,
                                }),
                                source="properties_sync",
                            )
                            stats["conflicts"] += 1
                            continue
                    else:
                        worker = Worker.objects.create(
                            first_name=first_name,
                            middle_name=middle_name,
                            last_name=last_name,
                            category="MWA",
                            employment_status="active",
                        )
                        stats["workers"] += 1

                    # ==================================================
                    # D. ADMIN BUILDING
                    # ==================================================
                    building_name = hu.property.name if hu.property else "Unknown Building"
                    building_address = hu.property.address if hu.property else ""

                    building, created = AdminBuilding.objects.get_or_create(
                        name=building_name,
                        defaults={"address": building_address}
                    )
                    if created:
                        stats["buildings"] += 1

                    # ==================================================
                    # E. OFFICE
                    # ==================================================
                    office_name = f"{department.name} Office"

                    office, created = Office.objects.get_or_create(
                        building=building,
                        name=office_name,
                        defaults={"department": department}
                    )
                    if created:
                        stats["offices"] += 1

                    # ==================================================
                    # F. OFFICE ASSIGNMENT
                    # ==================================================
                    if not WorkerOfficeAssignment.objects.filter(
                        worker=worker,
                        office=office,
                        end_date__isnull=True
                    ).exists():
                        WorkerOfficeAssignment.objects.create(
                            worker=worker,
                            office=office,
                            is_primary=True,
                            start_date=timezone.now().date()
                        )
                        stats["assignments"] += 1

                    # ==================================================
                    # G. HOUSING ASSIGNMENT
                    # ==================================================
                    if not HousingUnitAssignment.objects.filter(
                        worker=worker,
                        housing_unit=hu,
                        is_current=True
                    ).exists():
                        HousingUnitAssignment.objects.create(
                            worker=worker,
                            housing_unit=hu,
                            is_current=True,
                            start_date=timezone.now().date()
                        )

            # --------------------------------------------------
            # FINALIZE SYNC RUN
            # --------------------------------------------------
            sync_run.departments_created = stats["departments"]
            sync_run.sections_created = stats["sections"]
            sync_run.workers_created = stats["workers"]
            sync_run.buildings_created = stats["buildings"]
            sync_run.offices_created = stats["offices"]
            sync_run.assignments_created = stats["assignments"]
            sync_run.conflicts_detected = stats["conflicts"]

            if stats["conflicts"] > 0:
                sync_run.status = "partial"

        except Exception as e:
            sync_run.status = "failed"
            sync_run.notes = str(e)
            raise

        finally:
            sync_run.finished_at = timezone.now()
            sync_run.duration_ms = int((time.time() - start_time) * 1000)
            sync_run.save()

        # --------------------------------------------------
        # REPORT
        # --------------------------------------------------
        self.stdout.write(self.style.SUCCESS("\nSYNC COMPLETE"))
        self.stdout.write("-" * 60)
        self.stdout.write(f"Departments created : {stats['departments']}")
        self.stdout.write(f"Sections created    : {stats['sections']}")
        self.stdout.write(f"Workers created     : {stats['workers']}")
        self.stdout.write(f"Buildings created   : {stats['buildings']}")
        self.stdout.write(f"Offices created     : {stats['offices']}")
        self.stdout.write(f"Assignments created : {stats['assignments']}")
        self.stdout.write(f"Conflicts logged    : {stats['conflicts']}")
        self.stdout.write("-" * 60)
