# national/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class District(models.Model):
    dcode = models.CharField(max_length=5, unique=True)  # ex: 01009
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.dcode} - {self.name or 'Unnamed'}"


class Local(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="locals")
    lcode = models.CharField(max_length=20)
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("district", "lcode")

    def __str__(self):
        return f"{self.lcode} - {self.name or 'Unnamed'}"


class Report(models.Model):
    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name="reports")
    year = models.IntegerField()
    filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    file_hash = models.CharField(max_length=128, blank=True)

    class Meta:
        unique_together = ("local", "year")

    def __str__(self):
        return f"{self.local.name or self.local.lcode} - {self.year}"


# -------------------------
# PAGE 1 - Buildings
# -------------------------
class Chapel(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="chapels")
    year = models.IntegerField(null=True, blank=True)
    dcode = models.CharField(max_length=5, blank=True)
    lcode = models.CharField(max_length=10, blank=True)
    lokal = models.CharField(max_length=255, blank=True)

    chapel_class = models.CharField(max_length=50, blank=True)   # A-1/A-2/A-3
    seating_capacity = models.IntegerField(null=True, blank=True)
    offered = models.BooleanField(default=False)
    date_offered = models.DateField(null=True, blank=True)
    date_built = models.DateField(null=True, blank=True)
    funded_by = models.CharField(max_length=128, blank=True)

    original_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    last_year_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    add_construction = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    add_renovation = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    add_general_repair = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    add_others = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_added = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    deduction_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    deduction_reason = models.CharField(max_length=255, blank=True)
    total_cost_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Chapel {self.chapel_class} ({self.lokal})"


class PastoralHouse(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="pastoral_houses")
    description = models.CharField(max_length=255, blank=True)
    house_class = models.CharField(max_length=50, blank=True)
    date_built = models.DateField(null=True, blank=True)

    old_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    add_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    sub_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"PastoralHouse {self.description}"


class OfficeBuilding(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="offices")
    office_name = models.CharField(max_length=255, blank=True)
    office_class = models.CharField(max_length=50, blank=True)
    date_built = models.DateField(null=True, blank=True)

    old_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    add_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    sub_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Office {self.office_name}"


class OtherBuilding(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="other_buildings")
    building_name = models.CharField(max_length=255, blank=True)
    building_class = models.CharField(max_length=50, blank=True)
    date_built = models.DateField(null=True, blank=True)

    add_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    sub_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.building_name}"


class Page1Summary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="page1_summary")
    total_chapels = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_pastoral = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_offices = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_other_buildings = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    computed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Page1Summary for {self.report}"


# -------------------------
# PAGE 2 - Items
# -------------------------
class Item(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="items")

    kaukulan = models.CharField(max_length=255, blank=True, null=True)  # place / section
    iin_code = models.CharField(max_length=50, blank=True, null=True)
    date_received = models.DateField(null=True, blank=True)

    qty = models.IntegerField(null=True, blank=True)
    item_name = models.CharField(max_length=255)

    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)

    unit_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.kaukulan or ''} - {self.item_name} ({self.qty})"


class ItemsSummary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="items_summary")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"ItemsSummary for {self.report}"


# -------------------------
# PAGE 3 - Items Added (approved)
# -------------------------
class ItemAdded(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="items_added")
    kaukulan = models.CharField(max_length=255, blank=True, null=True)
    iin_code = models.CharField(max_length=50, blank=True, null=True)
    date_received = models.DateField(null=True, blank=True)

    qty = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)

    unit_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    approval_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Added: {self.brand or ''} ({self.qty})"


class ItemAddedSummary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="items_added_summary")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


# -------------------------
# PAGE 4 - Items Removed
# -------------------------
class ItemRemoved(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="items_removed")
    source_place = models.CharField(max_length=255, blank=True, null=True)
    iin_code = models.CharField(max_length=50, blank=True, null=True)
    date_received = models.DateField(null=True, blank=True)

    qty = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    reason = models.CharField(max_length=255, blank=True, null=True)
    approval_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Removed: {self.iin_code} ({self.qty})"


class ItemRemovedSummary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="items_removed_summary")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


# -------------------------
# PAGE 5 - Land, Plants, Vehicles
# -------------------------
class Land(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="lands")
    address = models.CharField(max_length=255)
    area_sqm = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    date_acquired = models.DateField(null=True, blank=True)
    value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    building_on_land = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=20, default="existing")  # existing, added, removed

    def __str__(self):
        return f"Land: {self.address}"


class LandSummary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="land_summary")
    total_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    no_land_type = models.CharField(max_length=50, blank=True, null=True)  # hiram / rental
    owner = models.CharField(max_length=255, blank=True, null=True)
    contract_years = models.CharField(max_length=50, blank=True, null=True)
    contract_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


class Plant(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="plants")
    name = models.CharField(max_length=255)
    plant_type = models.CharField(max_length=1, blank=True, null=True)  # a or b

    last_year_qty = models.IntegerField(null=True, blank=True)
    last_year_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    this_year_qty = models.IntegerField(null=True, blank=True)
    this_year_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    sub_qty = models.IntegerField(null=True, blank=True)
    sub_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    total_value_current = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class PlantSummary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="plant_summary")
    total_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


class Vehicle(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="vehicles")
    make_type = models.CharField(max_length=255)
    plate_number = models.CharField(max_length=50, blank=True, null=True)
    year_model = models.IntegerField(null=True, blank=True)
    date_purchased = models.DateField(null=True, blank=True)

    assigned_user = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)

    cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=20, default="existing")  # existing, added, removed

    def __str__(self):
        return f"Vehicle: {self.make_type} - {self.plate_number}"


class VehicleSummary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="vehicle_summary")
    total_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


# -------------------------
# REPORT AGGREGATE SUMMARY
# -------------------------
class ReportSummary(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="summary")
    p1_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    p2_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    p3_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    p4_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    p5_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_summary = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
