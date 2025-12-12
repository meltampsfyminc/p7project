# national/management/commands/import_national.py
import re
from decimal import Decimal, InvalidOperation
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
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
from property_management.national import models

User = get_user_model()

NUM_RE = re.compile(r'-?\d[\d,\.()]*')

def clean_num(v):
    if v is None: return None
    s = str(v).strip()
    if s == '': return None
    s = s.replace('₱','').replace(',','').replace('–','-').replace('—','-')
    s = s.replace('(', '-').replace(')', '')
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None

def last_numeric_values_in_row(row):
    nums = []
    for v in row:
        n = clean_num(v)
        if n is not None:
            nums.append(n)
    return nums

def is_kaukulan_label(row):
    # simple heuristic: first cell has letters and most other first few cells are empty
    first = str(row[0]).strip()
    if not first: 
        return False
    # if other cells in row are mostly empty and first is alphabetic text -> label
    nonempty = sum(1 for c in row[1:6] if str(c).strip())
    if nonempty == 0 and re.match(r'^[A-Za-zÑñ\s]+$', first):
        # also ignore very long texts that look like notes
        return len(first) < 120
    return False

def find_sheet(xls, names):
    for s in xls.sheet_names:
        up = s.upper()
        for n in names:
            if n in up:
                return s
    return None

class Command(BaseCommand):
    help = "Import P-7 workbook (PAGE 1..PAGE 5) into national app models."

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True)
        parser.add_argument('--user', type=int, required=False)

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts['file']
        user_id = opts.get('user')
        uploader = None
        if user_id:
            try:
                uploader = User.objects.get(pk=int(user_id))
            except Exception:
                uploader = None

        xls = pd.ExcelFile(path)

        # Attempt to extract year, dcode, lcode, lokal name from entire workbook
        raw_concat = []
        for s in xls.sheet_names:
            df0 = pd.read_excel(xls, sheet_name=s, header=None, dtype=str).fillna('')
            raw_concat.append(df0.astype(str).values.flatten())
        bigtext = " ".join([str(x) for block in raw_concat for x in block])

        year_m = re.search(r'\b(20\d{2})\b', bigtext)
        year = int(year_m.group(1)) if year_m else None

        # quick scan for dcode/lcode/lokal
        dcode = None; lcode=None; lokal_name=None
        for s in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=s, header=None, dtype=str).fillna('')
            for i, row in df.iterrows():
                rowtext = " ".join([str(c) for c in row[:10]]).upper()
                if 'DCODE' in rowtext or 'DISTRICT CODE' in rowtext:
                    toks = [str(c).strip() for c in row if str(c).strip()]
                    for t in toks:
                        if re.match(r'^\d+$', t):
                            dcode = t.zfill(5)
                            break
                if 'LCODE' in rowtext or 'LOCAL CODE' in rowtext or 'LOKAL' in rowtext:
                    toks = [str(c).strip() for c in row if str(c).strip()]
                    if toks:
                        lcode = toks[-1]
                        lokal_name = " ".join(toks[1:]) if len(toks)>1 else toks[0]
            if dcode and lcode:
                break

        if not dcode:
            dcode = '00000'
        district, _ = District.objects.get_or_create(dcode=dcode, defaults={'name': ''})
        local, _ = Local.objects.get_or_create(district=district, lcode=lcode or '000', defaults={'name': lokal_name or ''})
        report, created = Report.objects.get_or_create(local=local, year=year or 0, defaults={'filename': path, 'uploaded_by': uploader})

        # ------------------------
        # PAGE 1 (BUILDINGS)
        # ------------------------
        sheet1 = find_sheet(xls, ['PAGE 1','PAGE1','PAGE_1'])
        if sheet1:
            df1 = pd.read_excel(xls, sheet_name=sheet1, header=None, dtype=str).fillna('')
            # heuristic scan: detect "CHAPEL" section, "PASTORAL", "OFFICE", "IBA PANG"
            section = None
            for idx, row in df1.iterrows():
                row_txt = " ".join([str(c) for c in row[:8]]).upper()
                if any(k in row_txt for k in ['KAPILYA','CHAPEL','A.']):
                    section = 'chapel'
                    continue
                if any(k in row_txt for k in ['PASTORAL','RESIDENTIAL','B.']):
                    section = 'pastoral'
                    continue
                if any(k in row_txt for k in ['OPISINA','OFFICE','C.']):
                    section = 'office'
                    continue
                if any(k in row_txt for k in ['IBA PANG MGA GUSALI','PUMP HOUSE','GUARD HOUSE','D.']):
                    section = 'other'
                if 'KABUUANG HALAGA' in row_txt or 'TOTAL' in row_txt:
                    nums = last_numeric_values_in_row(row.tolist())
                    if nums:
                        Page1Summary.objects.update_or_create(report=report, defaults={'grand_total': nums[-1]})
                    continue

                if section == 'chapel':
                    # create chapel entry when row contains a class or numeric net
                    if re.search(r'\bA-?\d\b|\bCONCRETE\b|\bKAPILYA\b', row_txt) or last_numeric_values_in_row(row.tolist()):
                        nums = last_numeric_values_in_row(row.tolist())
                        net = nums[-1] if len(nums)>=1 else None
                        deduction = nums[-2] if len(nums)>=2 else None
                        total_added = nums[-3] if len(nums)>=3 else None
                        last_year = nums[1] if len(nums)>=2 else None
                        original = nums[0] if len(nums)>=1 else None
                        Chapel.objects.create(
                            report=report,
                            year=year,
                            dcode=dcode,
                            lcode=lcode or '',
                            lokal=local.name or lokal_name or '',
                            chapel_class=str(row[0])[:50],
                            original_cost=original,
                            last_year_cost=last_year,
                            total_added=total_added,
                            deduction_amount=deduction,
                            total_cost_this_year=net
                        )
                elif section == 'pastoral':
                    nums = last_numeric_values_in_row(row.tolist())
                    text = str(row[0]).strip()
                    if text and nums:
                        old = nums[0] if len(nums)>=1 else None
                        add = nums[-2] if len(nums)>=2 else None
                        total = nums[-1] if len(nums)>=1 else None
                        PastoralHouse.objects.create(report=report, description=text[:255], old_cost=old, add_this_year=add, total_cost=total)
                elif section == 'office':
                    nums = last_numeric_values_in_row(row.tolist())
                    text = str(row[0]).strip()
                    if text and nums:
                        old = nums[0] if len(nums)>=1 else None
                        add = nums[-2] if len(nums)>=2 else None
                        total = nums[-1] if len(nums)>=1 else None
                        OfficeBuilding.objects.create(report=report, office_name=text[:255], old_cost=old, add_this_year=add, total_cost=total)
                elif section == 'other':
                    nums = last_numeric_values_in_row(row.tolist())
                    text = str(row[0]).strip()
                    if text and nums:
                        total = nums[-1] if len(nums)>=1 else None
                        add = nums[-2] if len(nums)>=2 else None
                        OtherBuilding.objects.create(report=report, building_name=text[:255], add_this_year=add, total_cost=total)

            # compute page1 totals
            total_chapels = Chapel.objects.filter(report=report).aggregate(total=models.Sum('total_cost_this_year'))['total'] or Decimal(0)
            total_pastoral = PastoralHouse.objects.filter(report=report).aggregate(total=models.Sum('total_cost'))['total'] or Decimal(0)
            total_offices = OfficeBuilding.objects.filter(report=report).aggregate(total=models.Sum('total_cost'))['total'] or Decimal(0)
            total_other = OtherBuilding.objects.filter(report=report).aggregate(total=models.Sum('total_cost'))['total'] or Decimal(0)
            grand = total_chapels + total_pastoral + total_offices + total_other
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
        sheet2 = find_sheet(xls, ['PAGE 2','PAGE2','PAGE_2'])
        if sheet2:
            df2 = pd.read_excel(xls, sheet_name=sheet2, header=None, dtype=str).fillna('')
            current_kaukulan = None
            items_created = 0
            for idx, row in df2.iterrows():
                # detect kaukulan label
                if is_kaukulan_label(row.tolist()):
                    current_kaukulan = str(row[0]).strip()
                    continue
                # item rows: heuristics — require at least item name and numeric amount
                row_list = [str(x).strip() for x in row.tolist()]
                nums = last_numeric_values_in_row(row.tolist())
                # attempt mapping by positions: [IIN, Date, Qty, Item, Brand, Model, Make, Color, Size, Serial, Unit Price, Amount, Remarks]
                iin = row_list[0] or None
                date_received = row_list[1] or None
                qty = None
                try:
                    qty = int(row_list[2]) if row_list[2] else None
                except:
                    qty = None
                item_name = row_list[3] if len(row_list) > 3 else None
                brand = row_list[4] if len(row_list) > 4 else None
                model = row_list[5] if len(row_list) > 5 else None
                make = row_list[6] if len(row_list) > 6 else None
                color = row_list[7] if len(row_list) > 7 else None
                size = row_list[8] if len(row_list) > 8 else None
                serial = row_list[9] if len(row_list) > 9 else None
                unit_price = clean_num(row_list[10]) if len(row_list) > 10 else (nums[-2] if len(nums)>=2 else None)
                amount = clean_num(row_list[11]) if len(row_list) > 11 else (nums[-1] if len(nums)>=1 else None)
                remarks = row_list[12] if len(row_list) > 12 else ''
                # minimal check: item_name not empty and amount exists
                if item_name and amount is not None:
                    Item.objects.create(
                        report=report,
                        kaukulan=current_kaukulan,
                        iin_code=iin,
                        date_received=None if not date_received else date_received,
                        qty=qty,
                        item_name=item_name,
                        brand=brand,
                        model=model,
                        make=make,
                        color=color,
                        size=size,
                        serial_number=serial,
                        unit_price=unit_price,
                        amount=amount,
                        remarks=remarks
                    )
                    items_created += 1
            total_amount = Item.objects.filter(report=report).aggregate(total=models.Sum('amount'))['total'] or Decimal(0)
            ItemsSummary.objects.update_or_create(report=report, defaults={'total_amount': total_amount})

        # ------------------------
        # PAGE 3 (ADDED ITEMS)
        # ------------------------
        sheet3 = find_sheet(xls, ['PAGE 3','PAGE3','PAGE_3'])
        if sheet3:
            df3 = pd.read_excel(xls, sheet_name=sheet3, header=None, dtype=str).fillna('')
            current_kaukulan = None
            created_cnt = 0
            for idx, row in df3.iterrows():
                if is_kaukulan_label(row.tolist()):
                    current_kaukulan = str(row[0]).strip()
                    continue
                row_list = [str(x).strip() for x in row.tolist()]
                nums = last_numeric_values_in_row(row.tolist())
                item_name = row_list[3] if len(row_list)>3 else None
                if item_name and nums:
                    amount = nums[-1] if nums else None
                    qty = None
                    try:
                        qty = int(row_list[2]) if len(row_list)>2 and row_list[2] else None
                    except:
                        qty = None
                    ItemAdded.objects.create(
                        report=report,
                        kaukulan=current_kaukulan,
                        iin_code=row_list[0] if len(row_list)>0 else None,
                        date_received=None if not row_list[1] else row_list[1],
                        qty=qty,
                        brand=row_list[4] if len(row_list)>4 else None,
                        make=row_list[5] if len(row_list)>5 else None,
                        color=row_list[6] if len(row_list)>6 else None,
                        size=row_list[7] if len(row_list)>7 else None,
                        serial_number=row_list[8] if len(row_list)>8 else None,
                        unit_price=clean_num(row_list[10]) if len(row_list)>10 else (nums[-2] if len(nums)>=2 else None),
                        amount=amount,
                        approval_number=row_list[11] if len(row_list)>11 else None
                    )
                    created_cnt += 1
            total_added = ItemAdded.objects.filter(report=report).aggregate(total=models.Sum('amount'))['total'] or Decimal(0)
            ItemAddedSummary.objects.update_or_create(report=report, defaults={'total_amount': total_added})

        # ------------------------
        # PAGE 4 (REMOVED ITEMS)
        # ------------------------
        sheet4 = find_sheet(xls, ['PAGE 4','PAGE4','PAGE_4'])
        if sheet4:
            df4 = pd.read_excel(xls, sheet_name=sheet4, header=None, dtype=str).fillna('')
            created_cnt = 0
            for idx, row in df4.iterrows():
                if is_kaukulan_label(row.tolist()):  # sometimes source place label appears
                    continue
                row_list = [str(x).strip() for x in row.tolist()]
                nums = last_numeric_values_in_row(row.tolist())
                # mapping: [source_place, IIN, Date, Qty, UnitPrice, Amount, Reason, Approval]
                source_place = row_list[0] if row_list[0] else None
                iin = row_list[1] if len(row_list)>1 else None
                qty = None
                try:
                    qty = int(row_list[3]) if len(row_list)>3 and row_list[3] else None
                except:
                    qty = None
                unit_price = clean_num(row_list[4]) if len(row_list)>4 else (nums[-2] if len(nums)>=2 else None)
                amount = clean_num(row_list[5]) if len(row_list)>5 else (nums[-1] if len(nums)>=1 else None)
                reason = row_list[6] if len(row_list)>6 else None
                approval = row_list[7] if len(row_list)>7 else None
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
                    created_cnt += 1
            total_removed = ItemRemoved.objects.filter(report=report).aggregate(total=models.Sum('amount'))['total'] or Decimal(0)
            ItemRemovedSummary.objects.update_or_create(report=report, defaults={'total_amount': total_removed})

        # ------------------------
        # PAGE 5 (LANDS / PLANTS / VEHICLES)
        # ------------------------
        sheet5 = find_sheet(xls, ['PAGE 5','PAGE5','PAGE_5'])
        if sheet5:
            df5 = pd.read_excel(xls, sheet_name=sheet5, header=None, dtype=str).fillna('')
            # We need to detect sub-sections: Land, Plants, Vehicles
            section = None
            for idx, row in df5.iterrows():
                row_txt = " ".join([str(c) for c in row[:8]]).upper()
                if any(k in row_txt for k in ['LUPA','LAND']):
                    section = 'land'; continue
                if any(k in row_txt for k in ['PANANIM','PLANT','PANAMIN','PANANIM']):
                    section = 'plant'; continue
                if any(k in row_txt for k in ['SASAKYAN','VEHICLE','CAR','MOTOR']):
                    section = 'vehicle'; continue

                if section == 'land':
                    # detect rows with address + area + date + value
                    row_list = [str(x).strip() for x in row.tolist()]
                    # heuristic: address present and numeric value somewhere
                    nums = last_numeric_values_in_row(row.tolist())
                    if row_list[0] and nums:
                        # assume: address, area, date, value, building, remarks
                        addr = row_list[0]
                        area = clean_num(row_list[1]) if len(row_list)>1 else None
                        date_acq = None if len(row_list)<=2 or not row_list[2] else row_list[2]
                        value = clean_num(row_list[3]) if len(row_list)>3 else (nums[-1] if nums else None)
                        building_on = row_list[4] if len(row_list)>4 else ''
                        remarks = row_list[5] if len(row_list)>5 else ''
                        Land.objects.create(report=report, address=addr[:255], area_sqm=area, date_acquired=None if not date_acq else date_acq, value=value, building_on_land=building_on, remarks=remarks)
                elif section == 'plant':
                    row_list = [str(x).strip() for x in row.tolist()]
                    nums = last_numeric_values_in_row(row.tolist())
                    if row_list[0] and nums:
                        # mapping heuristic: name | type | last_qty | last_val | now_qty | now_val | sub_qty | sub_val | total
                        name = row_list[0]
                        plant_type = row_list[1] if len(row_list)>1 else None
                        last_qty = int(row_list[2]) if len(row_list)>2 and row_list[2].isdigit() else None
                        last_val = clean_num(row_list[3]) if len(row_list)>3 else None
                        now_qty = int(row_list[4]) if len(row_list)>4 and row_list[4].isdigit() else None
                        now_val = clean_num(row_list[5]) if len(row_list)>5 else None
                        sub_qty = int(row_list[6]) if len(row_list)>6 and row_list[6].isdigit() else None
                        sub_val = clean_num(row_list[7]) if len(row_list)>7 else None
                        total_val = clean_num(row_list[8]) if len(row_list)>8 else (nums[-1] if nums else None)
                        Plant.objects.create(report=report, name=name[:255], plant_type=plant_type, last_year_qty=last_qty, last_year_value=last_val, this_year_qty=now_qty, this_year_value=now_val, sub_qty=sub_qty, sub_value=sub_val, total_value_current=total_val)
                elif section == 'vehicle':
                    row_list = [str(x).strip() for x in row.tolist()]
                    nums = last_numeric_values_in_row(row.tolist())
                    if row_list[0] and nums:
                        make_type = row_list[0]
                        plate = row_list[1] if len(row_list)>1 else None
                        year_model = None
                        try:
                            year_model = int(row_list[2]) if len(row_list)>2 and row_list[2].isdigit() else None
                        except:
                            year_model = None
                        date_purchased = None if len(row_list)<=3 or not row_list[3] else row_list[3]
                        assigned_user = row_list[4] if len(row_list)>4 else None
                        designation = row_list[5] if len(row_list)>5 else None
                        cost = clean_num(row_list[6]) if len(row_list)>6 else (nums[-1] if nums else None)
                        Vehicle.objects.create(report=report, make_type=make_type[:255], plate_number=plate, year_model=year_model, date_purchased=None if not date_purchased else date_purchased, assigned_user=assigned_user, designation=designation, cost=cost)
            # compute land/plant/vehicle totals
            total_land = Land.objects.filter(report=report).aggregate(total=models.Sum('value'))['total'] or Decimal(0)
            total_plant = Plant.objects.filter(report=report).aggregate(total=models.Sum('total_value_current'))['total'] or Decimal(0)
            total_vehicle = Vehicle.objects.filter(report=report).aggregate(total=models.Sum('cost'))['total'] or Decimal(0)
            LandSummary.objects.update_or_create(report=report, defaults={'total_value': total_land})
            PlantSummary.objects.update_or_create(report=report, defaults={'total_value': total_plant})
            VehicleSummary.objects.update_or_create(report=report, defaults={'total_value': total_vehicle})

        # ------------------------
        # FINAL REPORT SUMMARY (aggregate pages)
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

        total_summary = p1_total + p2_total + p3_total - p4_total + p5_total

        ReportSummary.objects.update_or_create(report=report, defaults={
            'p1_total': p1_total,
            'p2_total': p2_total,
            'p3_total': p3_total,
            'p4_total': p4_total,
            'p5_total': p5_total,
            'total_summary': total_summary
        })

        self.stdout.write(self.style.SUCCESS(f"Import complete. Report={report}"))
