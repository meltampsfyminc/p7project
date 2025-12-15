# Run this in Django shell to diagnose issues
# python manage.py shell < diagnostic.py

from django.db.models import Sum
from decimal import Decimal
from national.models import (
    Report, District, Local,
    Chapel, PastoralHouse, OfficeBuilding, OtherBuilding,
    Item, ItemAdded, ItemRemoved,
    Land, Plant, Vehicle,
    Page1Summary, ItemsSummary, ItemAddedSummary, ItemRemovedSummary,
    LandSummary, PlantSummary, VehicleSummary, ReportSummary
)

print("=" * 70)
print("P7 IMPORT SYSTEM DIAGNOSTIC")
print("=" * 70)

# Get the latest report
report = Report.objects.latest('uploaded_at')
print(f"\nLatest Report: {report}")
print(f"  Year: {report.year}")
print(f"  Local: {report.local.name}")
print(f"  District: {report.local.district.name}")
print(f"  Uploaded: {report.uploaded_at}")

print("\n" + "=" * 70)
print("PAGE 1 - BUILDINGS")
print("=" * 70)

chapels = Chapel.objects.filter(report=report)
pastoral = PastoralHouse.objects.filter(report=report)
offices = OfficeBuilding.objects.filter(report=report)
other = OtherBuilding.objects.filter(report=report)

print(f"\nChapels: {chapels.count()}")
for chapel in chapels[:3]:
    print(f"  - {chapel.chapel_class}: ₱{chapel.total_cost_this_year or 0:,.2f}")

print(f"\nPastoral Houses: {pastoral.count()}")
for p in pastoral[:3]:
    print(f"  - {p.description}: ₱{p.total_cost or 0:,.2f}")

print(f"\nOffices: {offices.count()}")
for o in offices[:3]:
    print(f"  - {o.office_name}: ₱{o.total_cost or 0:,.2f}")

print(f"\nOther Buildings: {other.count()}")
for b in other[:3]:
    print(f"  - {b.building_name}: ₱{b.total_cost or 0:,.2f}")

# Check if Page1Summary exists and has data
try:
    p1_summary = report.page1_summary
    print(f"\n✅ Page1Summary EXISTS")
    print(f"  Total Chapels: ₱{p1_summary.total_chapels or 0:,.2f}")
    print(f"  Total Pastoral: ₱{p1_summary.total_pastoral or 0:,.2f}")
    print(f"  Total Offices: ₱{p1_summary.total_offices or 0:,.2f}")
    print(f"  Total Other: ₱{p1_summary.total_other_buildings or 0:,.2f}")
    print(f"  Grand Total: ₱{p1_summary.grand_total or 0:,.2f}")
except Page1Summary.DoesNotExist:
    print(f"\n❌ Page1Summary DOES NOT EXIST - needs to be created")

print("\n" + "=" * 70)
print("PAGE 2 - ITEMS")
print("=" * 70)

items = Item.objects.filter(report=report)
print(f"\nTotal Items: {items.count()}")

items_by_kaukulan = items.values('kaukulan').annotate(count=Sum('qty'), total=Sum('amount'))
for row in items_by_kaukulan[:5]:
    print(f"  {row['kaukulan'] or 'Unknown'}: {row['count'] or 0} items, ₱{row['total'] or 0:,.2f}")

# Check ItemsSummary
try:
    items_summary = report.items_summary
    print(f"\n✅ ItemsSummary EXISTS")
    print(f"  Total Amount: ₱{items_summary.total_amount or 0:,.2f}")
except ItemsSummary.DoesNotExist:
    print(f"\n❌ ItemsSummary DOES NOT EXIST - needs to be created")

print("\n" + "=" * 70)
print("PAGE 3 - ITEMS ADDED")
print("=" * 70)

added_items = ItemAdded.objects.filter(report=report)
print(f"\nTotal Added Items: {added_items.count()}")

if added_items.count() > 0:
    for item in added_items[:3]:
        print(f"  - {item.brand or 'N/A'}: {item.qty or 0} units @ ₱{item.unit_price or 0:,.2f} = ₱{item.amount or 0:,.2f}")
else:
    print("  No added items found")

# Check ItemAddedSummary
try:
    added_summary = report.items_added_summary
    print(f"\n✅ ItemAddedSummary EXISTS")
    print(f"  Total Amount: ₱{added_summary.total_amount or 0:,.2f}")
except ItemAddedSummary.DoesNotExist:
    print(f"\n❌ ItemAddedSummary DOES NOT EXIST - needs to be created")

print("\n" + "=" * 70)
print("PAGE 4 - ITEMS REMOVED")
print("=" * 70)

removed_items = ItemRemoved.objects.filter(report=report)
print(f"\nTotal Removed Items: {removed_items.count()}")

if removed_items.count() > 0:
    for item in removed_items[:3]:
        print(f"  - {item.source_place or 'N/A'}: {item.qty or 0} units, Reason: {item.reason or 'N/A'}")
else:
    print("  No removed items found")

# Check ItemRemovedSummary
try:
    removed_summary = report.items_removed_summary
    print(f"\n✅ ItemRemovedSummary EXISTS")
    print(f"  Total Amount: ₱{removed_summary.total_amount or 0:,.2f}")
except ItemRemovedSummary.DoesNotExist:
    print(f"\n❌ ItemRemovedSummary DOES NOT EXIST - needs to be created")

print("\n" + "=" * 70)
print("PAGE 5 - LAND, PLANTS, VEHICLES")
print("=" * 70)

lands = Land.objects.filter(report=report)
plants = Plant.objects.filter(report=report)
vehicles = Vehicle.objects.filter(report=report)

print(f"\nLands: {lands.count()}")
if lands.count() > 0:
    total_land = lands.aggregate(Sum('value'))['value__sum'] or Decimal(0)
    for land in lands[:3]:
        print(f"  - {land.address}: {land.area_sqm or 0} sqm, ₱{land.value or 0:,.2f}")
    print(f"  Total Land Value: ₱{total_land:,.2f}")

print(f"\nPlants: {plants.count()}")
if plants.count() > 0:
    total_plant = plants.aggregate(Sum('total_value_current'))['total_value_current__sum'] or Decimal(0)
    for plant in plants[:3]:
        print(f"  - {plant.name}: {plant.this_year_qty or 0} units, ₱{plant.total_value_current or 0:,.2f}")
    print(f"  Total Plant Value: ₱{total_plant:,.2f}")

print(f"\nVehicles: {vehicles.count()}")
if vehicles.count() > 0:
    total_vehicle = vehicles.aggregate(Sum('cost'))['cost__sum'] or Decimal(0)
    for vehicle in vehicles[:3]:
        print(f"  - {vehicle.make_type} ({vehicle.plate_number or 'N/A'}): ₱{vehicle.cost or 0:,.2f}")
    print(f"  Total Vehicle Value: ₱{total_vehicle:,.2f}")

# Check all summaries
try:
    land_summary = report.land_summary
    print(f"\n✅ LandSummary EXISTS: ₱{land_summary.total_value or 0:,.2f}")
except LandSummary.DoesNotExist:
    print(f"\n❌ LandSummary DOES NOT EXIST")

try:
    plant_summary = report.plant_summary
    print(f"✅ PlantSummary EXISTS: ₱{plant_summary.total_value or 0:,.2f}")
except PlantSummary.DoesNotExist:
    print(f"❌ PlantSummary DOES NOT EXIST")

try:
    vehicle_summary = report.vehicle_summary
    print(f"✅ VehicleSummary EXISTS: ₱{vehicle_summary.total_value or 0:,.2f}")
except VehicleSummary.DoesNotExist:
    print(f"❌ VehicleSummary DOES NOT EXIST")

print("\n" + "=" * 70)
print("AGGREGATE SUMMARY")
print("=" * 70)

try:
    summary = report.summary
    print(f"\n✅ ReportSummary EXISTS")
    print(f"  Page 1 Total: ₱{summary.p1_total or 0:,.2f}")
    print(f"  Page 2 Total: ₱{summary.p2_total or 0:,.2f}")
    print(f"  Page 3 Total: ₱{summary.p3_total or 0:,.2f}")
    print(f"  Page 4 Total: ₱{summary.p4_total or 0:,.2f}")
    print(f"  Page 5 Total: ₱{summary.p5_total or 0:,.2f}")
    print(f"  GRAND TOTAL: ₱{summary.total_summary or 0:,.2f}")
except ReportSummary.DoesNotExist:
    print(f"\n❌ ReportSummary DOES NOT EXIST")

print("\n" + "=" * 70)
print("SUMMARY CHECK")
print("=" * 70)

missing = []
try:
    report.page1_summary
except:
    missing.append("Page1Summary")

try:
    report.items_summary
except:
    missing.append("ItemsSummary")

try:
    report.items_added_summary
except:
    missing.append("ItemAddedSummary")

try:
    report.items_removed_summary
except:
    missing.append("ItemRemovedSummary")

try:
    report.land_summary
except:
    missing.append("LandSummary")

try:
    report.plant_summary
except:
    missing.append("PlantSummary")

try:
    report.vehicle_summary
except:
    missing.append("VehicleSummary")

try:
    report.summary
except:
    missing.append("ReportSummary")

if not missing:
    print("\n✅ ALL SUMMARIES EXIST AND ARE ACCESSIBLE")
else:
    print(f"\n⚠️  MISSING SUMMARIES: {', '.join(missing)}")
    print("\nTo fix, run the import with the fixed create_summaries() method:")
    print("  python manage.py import_national --file=P7_2024_Balayan.xlsx --user=1 --debug")

print("\n" + "=" * 70)
print("RELATIONSHIP TEST")
print("=" * 70)

# Test the fixed views.py pattern
try:
    p1_summary = report.page1_summary
    print("✅ report.page1_summary - Works correctly")
except Page1Summary.DoesNotExist:
    print("⚠️  report.page1_summary - Returns DoesNotExist (handled by views.py)")

try:
    items_summary = report.items_summary
    print("✅ report.items_summary - Works correctly")
except ItemsSummary.DoesNotExist:
    print("⚠️  report.items_summary - Returns DoesNotExist (handled by views.py)")

print("\n✅ If you see DoesNotExist errors above, that's NORMAL")
print("   The fixed views.py catches these exceptions and sets value to None")

print("\n" + "=" * 70)