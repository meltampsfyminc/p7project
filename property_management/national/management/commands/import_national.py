# national/management/commands/import_national.py
import re
from decimal import Decimal, InvalidOperation
import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.db import transaction, models as djmodels
from django.contrib.auth import get_user_model

from national.models import (
    District, Local, Report,
    Chapel, PastoralHouse, OfficeBuilding, OtherBuilding, Page1Summary,
    Item, ItemsSummary,
    ItemAdded, ItemAddedSummary,
    ItemRemoved, ItemRemovedSummary,
    Land, LandSummary, Plant, PlantSummary, Vehicle, VehicleSummary,
    ReportSummary
)

User = get_user_model()

# --- helpers -----------------------------------------------------------------

NUM_RE = re.compile(r'-?\d[\d,\.()]*')

def clean_num(v):
    """Convert a string or numeric to Decimal or None. Remove currency signs and commas."""
    if v is None:
        return None
    s = str(v).strip()
    if s == '':
        return None
    # Common cleanups
    s = s.replace('₱', '').replace('PHP', '').replace(',', '').replace('–', '-').replace('—', '-')
    s = s.replace('(', '-').replace(')', '')
    # Remove stray non-digit trailing characters
    # If there are extra spaces/newlines
    s = s.strip()
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        # attempt to find first numeric substring
        m = re.search(r'(-?\d[\d\.,]*)', s)
        if m:
            try:
                return Decimal(m.group(1).replace(',', ''))
            except Exception:
                return None
        return None

def last_numeric_values_in_row(row):
    """Return list of Decimal numbers found in row cells (left->right)."""
    nums = []
    for v in row:
        n = clean_num(v)
        if n is not None:
            nums.append(n)
    return nums

def is_kaukulan_label(row):
    """Heuristic: treat a row as a label for section if first cell is short text and next few cells empty."""
    try:
        first = str(row[0]).strip()
    except Exception:
        return False
    if not first:
        return False
    # Not accept long paragraph lines (to avoid the footer paragraph being considered a label)
    if len(first) > 120:
        return False
    # If the first cell is alphabetic-ish and following cells empty
    nonempty = sum(1 for c in row[1:6] if str(c).strip())
    # basic alphabetic check (allowing Filipino letters and hyphens)
    if re.match(r'^[A-Za-zÑñ\-\s\.]+$', first) and nonempty == 0:
        return True
    return False

def find_sheet(xls, names):
    """Find first sheet whose uppercase name contains any of 'names' entries."""
    for s in xls.sheet_names:
        up = s.upper()
        for n in names:
            if n in up:
                return s
    return None

def extract_digits(s):
    if s is None:
        return ''
    return ''.join(ch for ch in str(s) if ch.isdigit())

# -----------------------------------------------------------------------------


class Command(BaseCommand):
    help = "Import P-7 Excel workbook (PAGE 1..PAGE 5) into national models."

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Path to the P-7 Excel file (.xls/.xlsx)')
        parser.add_argument('--user', type=int, required=False, help='Uploader user id')
        parser.add_argument('--debug', action='store_true', help='Enable debug prints')

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts['file']
        debug = opts.get('debug', False)
        user_id = opts.get('user')
        uploader = None
        if user_id:
            try:
                uploader = User.objects.get(pk=int(user_id))
            except Exception:
                uploader = None

        if not os.path.exists(path):
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        try:
            xls = pd.ExcelFile(path)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read Excel file: {e}"))
            return

        # Build bigtext to search for year quickly
        raw_concat = []
        for s in xls.sheet_names:
            try:
                df0 = pd.read_excel(xls, sheet_name=s, header=None, dtype=str).fillna('')
                raw_concat.append(df0.astype(str).values.flatten())
            except Exception:
                continue
        bigtext = " ".join([str(x) for block in raw_concat for x in block])

        # Detect year (first 20xx)
        year_m = re.search(r'\b(20\d{2})\b', bigtext)
        year = int(year_m.group(1)) if year_m else None

        # ----------------------------
        # Safe header extraction for dcode/lcode/lokal
        # ----------------------------
        dcode = None
        lcode = None
        lokal_name = None

        # Search each sheet for structured patterns
        for s in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=s, header=None, dtype=str).fillna('')
            except Exception:
                continue

            for idx, row in df.iterrows():
                row_cells = [str(c).strip() for c in row.tolist()]
                rowtext = " ".join(row_cells).upper()

                # District code detection: a 5-digit number is likely dcode
                if not dcode:
                    m = re.search(r'\b(\d{5})\b', rowtext)
                    if m:
                        # extra check: ensure this is not part of a long paragraph
                        if len(rowtext) < 150:
                            dcode = m.group(1)

                # LCODE detection (explicit label)
                if not lcode and ('LCODE' in rowtext or 'LOCAL CODE' in rowtext):
                    # Prefer to pull a short digit sequence from cells
                    for c in row_cells:
                        digits = extract_digits(c)
                        if digits and 1 <= len(digits) <= 4:
                            lcode = digits
                            break

                # LOKAL detection (explicit label)
                if not lokal_name and 'LOKAL' in rowtext:
                    # guard: avoid matching very long paragraphs
                    if len(rowtext) < 120:
                        # typical formats:
                        # ['LOKAL', 'Balayan', '003']
                        # or ['LOKAL: BALAYAN (003)']
                        # prefer the textual token which is not digits and not the literal 'LOKAL'
                        tokens = [c for c in row_cells if c and c.upper() != 'LOKAL' and c.upper() != 'LOKAL:']
                        if tokens:
                            # pick the first non-digit token as the name
                            for t in tokens:
                                if any(ch.isalpha() for ch in t):
                                    lokal_name = t
                                    break
                            # also attempt to extract lcode from tokens
                            if not lcode:
                                for t in reversed(tokens):
                                    digits = extract_digits(t)
                                    if digits and 1 <= len(digits) <= 4:
                                        lcode = digits
                                        break

                # also allow patterns like "LOCAL: NAME (003)" or "BALAYAN (003)"
                if not lcode or not lokal_name:
                    # search parentheses patterns e.g. "BALAYAN (003)"
                    m = re.search(r'([A-ZÁÉÍÓÚÑ0-9\-\s]{2,})\s*\(\s*(\d{1,4})\s*\)', rowtext)
                    if m:
                        candidate_name = m.group(1).strip()
                        candidate_code = m.group(2).strip()
                        if not lokal_name and len(candidate_name) < 80:
                            lokal_name = candidate_name.title()
                        if not lcode:
                            lcode = candidate_code

            if dcode and lcode and lokal_name:
                break

        # Fallbacks
        if not dcode:
            dcode = "00000"

        if not lcode:
            # attempt to find any small integer anywhere in bigtext near word LOCAL/LOKAL
            m = re.search(r'LOKAL\W+([A-Z0-9\(\)\s\-]+)', bigtext.upper())
            if m:
                maybe = m.group(1)
                digits = extract_digits(maybe)
                if digits and len(digits) <= 4:
                    lcode = digits

        # final cleaning
        lcode = (str(lcode).strip() or "000")
        # restrict length to 4 digits and digits only
        if not lcode.isdigit() or len(lcode) > 4:
            self.stdout.write(self.style.WARNING(f"Invalid or suspicious lcode '{lcode}' detected; forcing to '000'"))
            lcode = "000"

        # Normalize dcode to 5 digits
        dcode_digits = extract_digits(dcode)
        if not dcode_digits:
            dcode_digits = "00000"
        dcode = dcode_digits.zfill(5)

        # try to ensure lokal_name is not paragraph; if long, blank it
        if lokal_name:
            if len(str(lokal_name)) > 120:
                lokal_name = None

        if not lokal_name:
            # try to extract a first candidate locality from bigtext (first capitalized word sequence)
            m = re.search(r'\b([A-Z][a-zA-Z\-]{2,}(?:\s+[A-Z][a-zA-Z\-]{2,})?)\b', bigtext)
            if m:
                lokal_name = m.group(1).title()

        # Create or get district/local/report
        district, _ = District.objects.get_or_create(dcode=dcode, defaults={'name': ''})
        self.stdout.write(self.style.NOTICE(f"Using dcode={dcode}, lcode={lcode}, lokal='{lokal_name or ''}', year={year or ''}"))

        # ensure lcode length fits DB; Local.lcode is up to 20 in your model — still enforce short code
        lcode_short = lcode[:20]
        local, created_local = Local.objects.get_or_create(
            district=district,
            lcode=lcode_short,
            defaults={'name': lokal_name or ''}
        )

        report, created = Report.objects.get_or_create(
            local=local,
            year=year or 0,
            defaults={'filename': os.path.basename(path), 'uploaded_by': uploader}
        )

        # ------------------------
        # PAGE 1 (BUILDINGS)
        # ------------------------
        sheet1 = find_sheet(xls, ['PAGE 1', 'PAGE1', 'PAGE_1', 'BUILDING', 'GUSALI'])
        if sheet1:
            try:
                df1 = pd.read_excel(xls, sheet_name=sheet1, header=None, dtype=str).fillna('')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read PAGE1: {e}"))
                df1 = None
        else:
            df1 = None

        # Clear existing page1 entries for same report (optional - avoid duplicates on re-import)
        # (You can remove these deletes if you prefer incremental)
        Chapel.objects.filter(report=report).delete()
        PastoralHouse.objects.filter(report=report).delete()
        OfficeBuilding.objects.filter(report=report).delete()
        OtherBuilding.objects.filter(report=report).delete()

        if df1 is not None:
            section = None
            for idx, row in df1.iterrows():
                # combine first N columns for analysis
                row_txt = " ".join([str(c) for c in row[:8]]).upper()
                # detect headings
                if any(k in row_txt for k in ['KAPILYA', 'CHAPEL', 'A.']):
                    section = 'chapel'
                    continue
                if any(k in row_txt for k in ['PASTORAL', 'RESIDENTIAL', 'B.']):
                    section = 'pastoral'
                    continue
                if any(k in row_txt for k in ['OPISINA', 'OFFICE', 'C.']):
                    section = 'office'
                    continue
                if any(k in row_txt for k in ['IBA PANG', 'PUMP HOUSE', 'GUARD HOUSE', 'D.']):
                    section = 'other'
                    continue

                # totals row detection
                if 'KABUUANG HALAGA' in row_txt or 'TOTAL' in row_txt:
                    nums = last_numeric_values_in_row(row.tolist())
                    if nums:
                        Page1Summary.objects.update_or_create(report=report, defaults={'grand_total': nums[-1]})
                    continue

                # depending on section, parse row heuristically
                if section == 'chapel':
                    # if the row contains a class token or numeric values -> create chapel
                    if re.search(r'\bA-?\d\b|\bCONCRETE\b|\bKAPILYA\b', row_txt) or last_numeric_values_in_row(row.tolist()):
                        nums = last_numeric_values_in_row(row.tolist())
                        net = nums[-1] if len(nums) >= 1 else None
                        deduction = nums[-2] if len(nums) >= 2 else None
                        total_added = nums[-3] if len(nums) >= 3 else None
                        last_year = nums[1] if len(nums) >= 2 else None
                        original = nums[0] if len(nums) >= 1 else None
                        Chapel.objects.create(
                            report=report,
                            year=year,
                            dcode=dcode,
                            lcode=lcode_short,
                            lokal=local.name or lokal_name or '',
                            chapel_class=(str(row[0])[:50] if row[0] else ''),
                            original_cost=original,
                            last_year_cost=last_year,
                            total_added=total_added,
                            deduction_amount=deduction,
                            total_cost_this_year=net,
                            remarks=str(row[7])[:1000] if len(row) > 7 else ''
                        )
                elif section == 'pastoral':
                    nums = last_numeric_values_in_row(row.tolist())
                    text = str(row[0]).strip()
                    if text and nums:
                        old = nums[0] if len(nums) >= 1 else None
                        add = nums[-2] if len(nums) >= 2 else None
                        total = nums[-1] if len(nums) >= 1 else None
                        PastoralHouse.objects.create(report=report, description=text[:255], old_cost=old, add_this_year=add, total_cost=total)
                elif section == 'office':
                    nums = last_numeric_values_in_row(row.tolist())
                    text = str(row[0]).strip()
                    if text and nums:
                        old = nums[0] if len(nums) >= 1 else None
                        add = nums[-2] if len(nums) >= 2 else None
                        total = nums[-1] if len(nums) >= 1 else None
                        OfficeBuilding.objects.create(report=report, office_name=text[:255], old_cost=old, add_this_year=add, total_cost=total)
                elif section == 'other':
                    nums = last_numeric_values_in_row(row.tolist())
                    text = str(row[0]).strip()
                    if text and nums:
                        total = nums[-1] if len(nums) >= 1 else None
                        add = nums[-2] if len(nums) >= 2 else None
                        OtherBuilding.objects.create(report=report, building_name=text[:255], add_this_year=add, total_cost=total)

            # compute page1 totals
            total_chapels = Chapel.objects.filter(report=report).aggregate(total=djmodels.Sum('total_cost_this_year'))['total'] or Decimal(0)
            total_pastoral = PastoralHouse.objects.filter(report=report).aggregate(total=djmodels.Sum('total_cost'))['total'] or Decimal(0)
            total_offices = OfficeBuilding.objects.filter(report=report).aggregate(total=djmodels.Sum('total_cost'))['total'] or Decimal(0)
            total_other = OtherBuilding.objects.filter(report=report).aggregate(total=djmodels.Sum('total_cost'))['total'] or Decimal(0)
            grand = (total_chapels or Decimal(0)) + (total_pastoral or Decimal(0)) + (total_offices or Decimal(0)) + (total_other or Decimal(0))
            Page1Summary.objects.update_or_create(report=report, defaults={
                'total_chapels': total_chapels,
                'total_pastoral': total_pastoral,
                'total_offices': total_offices,
                'total_other_buildings': total_other,
                'grand_total': grand
            })

        # ------------------------
        # PAGE 2 (ITEMS)
        # ------------------------
        sheet2 = find_sheet(xls, ['PAGE 2', 'PAGE2', 'PAGE_2', 'ITEMS', 'KAGAMITAN'])
        items_created = 0
        if sheet2:
            try:
                df2 = pd.read_excel(xls, sheet_name=sheet2, header=None, dtype=str).fillna('')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read PAGE2: {e}"))
                df2 = None
        else:
            df2 = None

        # Clear previous items for the report to avoid duplicates
        Item.objects.filter(report=report).delete()

        if df2 is not None:
            current_kaukulan = None
            for idx, row in df2.iterrows():
                if is_kaukulan_label(row.tolist()):
                    current_kaukulan = str(row[0]).strip()
                    continue
                row_list = [str(x).strip() for x in row.tolist()]
                nums = last_numeric_values_in_row(row.tolist())

                # Mapping attempt: IIN, Date, Qty, Item, Brand, Model, Make, Color, Size, Serial, UnitPrice, Amount, Remarks
                iin = row_list[0] or None
                date_received = row_list[1] or None
                qty = None
                try:
                    qty = int(row_list[2]) if row_list[2] and row_list[2].isdigit() else None
                except Exception:
                    qty = None
                item_name = row_list[3] if len(row_list) > 3 else None
                brand = row_list[4] if len(row_list) > 4 else None
                model_val = row_list[5] if len(row_list) > 5 else None
                make = row_list[6] if len(row_list) > 6 else None
                color = row_list[7] if len(row_list) > 7 else None
                size = row_list[8] if len(row_list) > 8 else None
                serial = row_list[9] if len(row_list) > 9 else None
                unit_price = clean_num(row_list[10]) if len(row_list) > 10 else (nums[-2] if len(nums) >= 2 else None)
                amount = clean_num(row_list[11]) if len(row_list) > 11 else (nums[-1] if len(nums) >= 1 else None)
                remarks = row_list[12] if len(row_list) > 12 else ''

                if item_name and amount is not None:
                    Item.objects.create(
                        report=report,
                        kaukulan=current_kaukulan,
                        iin_code=iin,
                        date_received=None if not date_received else date_received,
                        qty=qty,
                        item_name=item_name[:255],
                        brand=brand,
                        model=model_val,
                        make=make,
                        color=color,
                        size=size,
                        serial_number=serial,
                        unit_price=unit_price,
                        amount=amount,
                        remarks=remarks[:255]
                    )
                    items_created += 1

            total_amount = Item.objects.filter(report=report).aggregate(total=djmodels.Sum('amount'))['total'] or Decimal(0)
            ItemsSummary.objects.update_or_create(report=report, defaults={'total_amount': total_amount})

        # ------------------------
        # PAGE 3 (ADDED ITEMS)
        # ------------------------
        sheet3 = find_sheet(xls, ['PAGE 3', 'PAGE3', 'PAGE_3', 'ADDED', 'NADADAG'])
        ItemAdded.objects.filter(report=report).delete()
        if sheet3:
            try:
                df3 = pd.read_excel(xls, sheet_name=sheet3, header=None, dtype=str).fillna('')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read PAGE3: {e}"))
                df3 = None
        else:
            df3 = None

        if df3 is not None:
            current_kaukulan = None
            created_add = 0
            for idx, row in df3.iterrows():
                if is_kaukulan_label(row.tolist()):
                    current_kaukulan = str(row[0]).strip()
                    continue
                row_list = [str(x).strip() for x in row.tolist()]
                nums = last_numeric_values_in_row(row.tolist())
                item_name = row_list[3] if len(row_list) > 3 else None
                if item_name and nums:
                    amount = nums[-1] if nums else None
                    qty = None
                    try:
                        qty = int(row_list[2]) if len(row_list) > 2 and row_list[2].isdigit() else None
                    except Exception:
                        qty = None
                    ItemAdded.objects.create(
                        report=report,
                        kaukulan=current_kaukulan,
                        iin_code=row_list[0] if len(row_list) > 0 else None,
                        date_received=None if not row_list[1] else row_list[1],
                        qty=qty,
                        brand=row_list[4] if len(row_list) > 4 else None,
                        make=row_list[5] if len(row_list) > 5 else None,
                        color=row_list[6] if len(row_list) > 6 else None,
                        size=row_list[7] if len(row_list) > 7 else None,
                        serial_number=row_list[8] if len(row_list) > 8 else None,
                        unit_price=clean_num(row_list[10]) if len(row_list) > 10 else (nums[-2] if len(nums) >= 2 else None),
                        amount=amount,
                        approval_number=row_list[11] if len(row_list) > 11 else None
                    )
                    created_add += 1
            total_added = ItemAdded.objects.filter(report=report).aggregate(total=djmodels.Sum('amount'))['total'] or Decimal(0)
            ItemAddedSummary.objects.update_or_create(report=report, defaults={'total_amount': total_added})

        # ------------------------
        # PAGE 4 (REMOVED ITEMS)
        # ------------------------
        sheet4 = find_sheet(xls, ['PAGE 4', 'PAGE4', 'PAGE_4', 'REMOVED', 'NABAWAS'])
        ItemRemoved.objects.filter(report=report).delete()
        if sheet4:
            try:
                df4 = pd.read_excel(xls, sheet_name=sheet4, header=None, dtype=str).fillna('')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read PAGE4: {e}"))
                df4 = None
        else:
            df4 = None

        if df4 is not None:
            created_removed = 0
            for idx, row in df4.iterrows():
                if is_kaukulan_label(row.tolist()):
                    continue
                row_list = [str(x).strip() for x in row.tolist()]
                nums = last_numeric_values_in_row(row.tolist())
                source_place = row_list[0] if row_list[0] else None
                iin = row_list[1] if len(row_list) > 1 else None
                qty = None
                try:
                    qty = int(row_list[3]) if len(row_list) > 3 and row_list[3].isdigit() else None
                except Exception:
                    qty = None
                unit_price = clean_num(row_list[4]) if len(row_list) > 4 else (nums[-2] if len(nums) >= 2 else None)
                amount = clean_num(row_list[5]) if len(row_list) > 5 else (nums[-1] if len(nums) >= 1 else None)
                reason = row_list[6] if len(row_list) > 6 else None
                approval = row_list[7] if len(row_list) > 7 else None
                if (iin or source_place) and amount is not None:
                    ItemRemoved.objects.create(
                        report=report,
                        source_place=source_place,
                        iin_code=iin,
                        date_received=None if not row_list[2] else row_list[2],
                        qty=qty,
                        unit_price=unit_price,
                        amount=amount,
                        reason=reason,
                        approval_number=approval
                    )
                    created_removed += 1
            total_removed = ItemRemoved.objects.filter(report=report).aggregate(total=djmodels.Sum('amount'))['total'] or Decimal(0)
            ItemRemovedSummary.objects.update_or_create(report=report, defaults={'total_amount': total_removed})

        # ------------------------
        # PAGE 5 (LANDS / PLANTS / VEHICLES)
        # ------------------------
        sheet5 = find_sheet(xls, ['PAGE 5', 'PAGE5', 'PAGE_5', 'LAND', 'LUPA', 'PANANIM', 'SASAKYAN'])
        # delete existing
        Land.objects.filter(report=report).delete()
        Plant.objects.filter(report=report).delete()
        Vehicle.objects.filter(report=report).delete()

        if sheet5:
            try:
                df5 = pd.read_excel(xls, sheet_name=sheet5, header=None, dtype=str).fillna('')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read PAGE5: {e}"))
                df5 = None
        else:
            df5 = None

        if df5 is not None:
            section = None
            for idx, row in df5.iterrows():
                row_txt = " ".join([str(c) for c in row[:8]]).upper()
                if any(k in row_txt for k in ['LUPA', 'LAND']):
                    section = 'land'; continue
                if any(k in row_txt for k in ['PANANIM', 'PLANT', 'PANAMIN']):
                    section = 'plant'; continue
                if any(k in row_txt for k in ['SASAKYAN', 'VEHICLE', 'CAR', 'MOTOR']):
                    section = 'vehicle'; continue

                if section == 'land':
                    row_list = [str(x).strip() for x in row.tolist()]
                    nums = last_numeric_values_in_row(row.tolist())
                    if row_list[0] and nums:
                        addr = row_list[0]
                        area = clean_num(row_list[1]) if len(row_list) > 1 else None
                        date_acq = None if len(row_list) <= 2 or not row_list[2] else row_list[2]
                        value = clean_num(row_list[3]) if len(row_list) > 3 else (nums[-1] if nums else None)
                        building_on = row_list[4] if len(row_list) > 4 else ''
                        remarks = row_list[5] if len(row_list) > 5 else ''
                        Land.objects.create(report=report, address=addr[:255], area_sqm=area, date_acquired=None if not date_acq else date_acq, value=value, building_on_land=building_on, remarks=remarks)
                elif section == 'plant':
                    row_list = [str(x).strip() for x in row.tolist()]
                    nums = last_numeric_values_in_row(row.tolist())
                    if row_list[0] and nums:
                        name = row_list[0]
                        plant_type = row_list[1] if len(row_list) > 1 else None
                        last_qty = int(row_list[2]) if len(row_list) > 2 and row_list[2].isdigit() else None
                        last_val = clean_num(row_list[3]) if len(row_list) > 3 else None
                        now_qty = int(row_list[4]) if len(row_list) > 4 and row_list[4].isdigit() else None
                        now_val = clean_num(row_list[5]) if len(row_list) > 5 else None
                        sub_qty = int(row_list[6]) if len(row_list) > 6 and row_list[6].isdigit() else None
                        sub_val = clean_num(row_list[7]) if len(row_list) > 7 else None
                        total_val = clean_num(row_list[8]) if len(row_list) > 8 else (nums[-1] if nums else None)
                        Plant.objects.create(report=report, name=name[:255], plant_type=plant_type, last_year_qty=last_qty, last_year_value=last_val, this_year_qty=now_qty, this_year_value=now_val, sub_qty=sub_qty, sub_value=sub_val, total_value_current=total_val)
                elif section == 'vehicle':
                    row_list = [str(x).strip() for x in row.tolist()]
                    nums = last_numeric_values_in_row(row.tolist())
                    if row_list[0] and nums:
                        make_type = row_list[0]
                        plate = row_list[1] if len(row_list) > 1 else None
                        year_model = None
                        try:
                            year_model = int(row_list[2]) if len(row_list) > 2 and row_list[2].isdigit() else None
                        except:
                            year_model = None
                        date_purchased = None if len(row_list) <= 3 or not row_list[3] else row_list[3]
                        assigned_user = row_list[4] if len(row_list) > 4 else None
                        designation = row_list[5] if len(row_list) > 5 else None
                        cost = clean_num(row_list[6]) if len(row_list) > 6 else (nums[-1] if nums else None)
                        Vehicle.objects.create(report=report, make_type=make_type[:255], plate_number=plate, year_model=year_model, date_purchased=None if not date_purchased else date_purchased, assigned_user=assigned_user, designation=designation, cost=cost)

            total_land = Land.objects.filter(report=report).aggregate(total=djmodels.Sum('value'))['total'] or Decimal(0)
            total_plant = Plant.objects.filter(report=report).aggregate(total=djmodels.Sum('total_value_current'))['total'] or Decimal(0)
            total_vehicle = Vehicle.objects.filter(report=report).aggregate(total=djmodels.Sum('cost'))['total'] or Decimal(0)
            LandSummary.objects.update_or_create(report=report, defaults={'total_value': total_land})
            PlantSummary.objects.update_or_create(report=report, defaults={'total_value': total_plant})
            VehicleSummary.objects.update_or_create(report=report, defaults={'total_value': total_vehicle})

        # ------------------------
        # FINAL AGGREGATE SUMMARY
        # ------------------------
        p1 = Page1Summary.objects.filter(report=report).first()
        p2 = ItemsSummary.objects.filter(report=report).first()
        p3 = ItemAddedSummary.objects.filter(report=report).first()
        p4 = ItemRemovedSummary.objects.filter(report=report).first()
        p5_land = LandSummary.objects.filter(report=report).first()
        p5_plant = PlantSummary.objects.filter(report=report).first()
        p5_vehicle = VehicleSummary.objects.filter(report=report).first()

        p1_total = p1.grand_total if p1 else Decimal(0)
        p2_total = p2.total_amount if p2 else Decimal(0)
        p3_total = p3.total_amount if p3 else Decimal(0)
        p4_total = p4.total_amount if p4 else Decimal(0)
        p5_total = (p5_land.total_value if p5_land else Decimal(0)) + (p5_plant.total_value if p5_plant else Decimal(0)) + (p5_vehicle.total_value if p5_vehicle else Decimal(0))

        total_summary = (p1_total or Decimal(0)) + (p2_total or Decimal(0)) + (p3_total or Decimal(0)) - (p4_total or Decimal(0)) + (p5_total or Decimal(0))

        ReportSummary.objects.update_or_create(report=report, defaults={
            'p1_total': p1_total,
            'p2_total': p2_total,
            'p3_total': p3_total,
            'p4_total': p4_total,
            'p5_total': p5_total,
            'total_summary': total_summary
        })

        self.stdout.write(self.style.SUCCESS(f"Import complete. Report={report}"))
