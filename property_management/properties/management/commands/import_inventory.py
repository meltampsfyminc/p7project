from django.core.management.base import BaseCommand
from datetime import datetime, date
import xlrd
import hashlib
import os

from properties.models import (
    Pamayanan,
    PamayananBuilding,
    HousingUnit,
    HousingUnitInventory,
    ImportedFile,
)


class Command(BaseCommand):
    help = "Import housing unit inventory from Excel (.xls)"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
        parser.add_argument("--force", action="store_true")

    # =====================================================
    # MAIN
    # =====================================================
    def handle(self, *args, **options):
        file_path = options["file_path"]
        force = options["force"]

        if not os.path.exists(file_path):
            self.stderr.write("❌ File not found")
            return

        # ---- FILE HASH / DUP CHECK
        file_hash = self._hash_file(file_path)
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)

        if not force and ImportedFile.objects.filter(file_hash=file_hash).exists():
            self.stdout.write("⚠ FILE ALREADY IMPORTED")
            return

        wb = xlrd.open_workbook(file_path)
        sheet = wb.sheet_by_index(0)

        # =====================================================
        # HEADER EXTRACTION (MERGED CELLS)
        # =====================================================
        occupant_name = self._cell(sheet, 4, 12)
        department = self._cell(sheet, 4, 33)
        section = self._cell(sheet, 4, 42)
        job_title = self._cell(sheet, 4, 54)

        housing_unit_name = self._cell(sheet, 5, 5)
        building_name = self._cell(sheet, 5, 14)
        floor = self._clean_floor(self._cell(sheet, 5, 20))
        unit_number = self._clean_unit(self._cell(sheet, 5, 25))
        address = self._cell(sheet, 5, 31)

        date_reported = self._parse_date(self._cell(sheet, 1, 47)) or date.today()

        # =====================================================
        # PAMAYANAN RULE (CRITICAL FIX)
        # =====================================================
        # SOLO Pamayanan (Abra, Tagumpay)
        if not floor:
            pamayanan_name = building_name or address
            building_obj = None
        else:
            # COMPOUND Pamayanan (LIG, High-rise)
            pamayanan_name = address or building_name

            building_obj = None

        pamayanan, _ = Pamayanan.objects.get_or_create(
            name=pamayanan_name,
            defaults={
                "owner": "The Church",
                "address": address,
                "city": "",
                "property_type": "Housing",
            },
        )

        if floor and building_name:
            building_obj, _ = PamayananBuilding.objects.get_or_create(
                pamayanan=pamayanan,
                name=building_name,
            )

        # =====================================================
        # HOUSING UNIT
        # =====================================================
        housing_unit, _ = HousingUnit.objects.get_or_create(
            pamayanan=pamayanan,
            building=building_obj,
            unit_number=unit_number or housing_unit_name,
            defaults={
                "housing_unit_name": housing_unit_name,
                "floor": floor or "",
                "address": address,
                "occupant_name": occupant_name,
                "department": department,
                "section": section,
                "job_title": job_title,
                "date_reported": date_reported,
            },
        )

        # =====================================================
        # INVENTORY ROWS
        # =====================================================
        created = 0
        skipped = 0

        for row in range(9, sheet.nrows):
            item_name = self._cell(sheet, row, 9)
            if not item_name:
                continue

            try:
                date_acquired = self._parse_date(self._cell(sheet, row, 3)) or date(2024, 1, 1)
                quantity = int(self._cell(sheet, row, 7) or 1)

                HousingUnitInventory.objects.create(
                    housing_unit=housing_unit,
                    item_name=item_name,
                    quantity=quantity,
                    date_acquired=date_acquired,
                    make=self._cell(sheet, row, 32),
                    color=self._cell(sheet, row, 37),
                    size=self._cell(sheet, row, 42),
                    remarks=self._cell(sheet, row, 52),
                )
                created += 1
            except Exception:
                skipped += 1

        # =====================================================
        # IMPORT RECORD (FIXED NULL file_size)
        # =====================================================
        ImportedFile.objects.update_or_create(
            file_hash=file_hash,
            defaults={
                "filename": filename,
                "file_size": file_size,
                "records_imported": created,
                "status": "success" if skipped == 0 else "partial",
                "error_message": f"Skipped {skipped} rows" if skipped else "",
            },
        )

        self.stdout.write("✅ IMPORT COMPLETE")
        self.stdout.write(f"Items created: {created}")
        self.stdout.write(f"Rows skipped: {skipped}")

    # =====================================================
    # HELPERS
    # =====================================================
    def _cell(self, sheet, r, c):
        try:
            val = sheet.cell_value(r, c)
            return str(val).strip() if val else ""
        except Exception:
            return ""

    def _clean_floor(self, val):
        if not val or "Floor" in val:
            return ""
        return val

    def _clean_unit(self, val):
        if not val or "Unit" in val:
            return ""
        return val

    def _parse_date(self, val):
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(val, fmt).date()
            except Exception:
                continue
        return None

    def _hash_file(self, path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
