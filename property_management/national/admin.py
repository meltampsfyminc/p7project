# national/admin.py
from django.contrib import admin
from django.db.models import Sum
from .models import (
    District, Local, Report,
    Chapel, PastoralHouse, OfficeBuilding, OtherBuilding, Page1Summary,
    Item, ItemsSummary,
    ItemAdded, ItemAddedSummary,
    ItemRemoved, ItemRemovedSummary,
    Land, LandSummary, Plant, PlantSummary, Vehicle, VehicleSummary,
    ReportSummary
)

# ====================
# CORE MODELS
# ====================
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('dcode', 'name')
    search_fields = ('dcode', 'name')
    ordering = ('dcode',)

@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ('lcode', 'name', 'district')
    list_filter = ('district',)
    search_fields = ('lcode', 'name', 'district__name')
    ordering = ('district', 'lcode')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('local', 'year', 'uploaded_at', 'uploaded_by', 'filename')
    list_filter = ('year', 'local__district', 'uploaded_at')
    search_fields = ('local__name', 'local__lcode', 'filename')
    ordering = ('-year', '-uploaded_at')
    raw_id_fields = ('local', 'uploaded_by')
    readonly_fields = ('file_hash', 'uploaded_at')

# ====================
# PAGE 1 - BUILDINGS
# ====================
@admin.register(Chapel)
class ChapelAdmin(admin.ModelAdmin):
    list_display = ('lokal', 'chapel_class', 'seating_capacity', 'date_built', 'total_cost_this_year')
    list_filter = ('chapel_class', 'report__year', 'offered')
    search_fields = ('lokal', 'dcode', 'lcode')
    raw_id_fields = ('report',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('report', 'year', 'dcode', 'lcode', 'lokal')
        }),
        ('Chapel Details', {
            'fields': ('chapel_class', 'seating_capacity', 'offered', 'date_offered', 
                      'date_built', 'funded_by')
        }),
        ('Cost Information', {
            'fields': ('original_cost', 'last_year_cost',
                      ('add_construction', 'add_renovation', 'add_general_repair', 'add_others'),
                      'total_added', 'deduction_amount', 'deduction_reason', 'total_cost_this_year')
        }),
        ('Remarks', {
            'fields': ('remarks',),
            'classes': ('collapse',)
        })
    )

@admin.register(PastoralHouse)
class PastoralHouseAdmin(admin.ModelAdmin):
    list_display = ('description', 'house_class', 'date_built', 'old_cost', 
                   'add_this_year', 'sub_this_year', 'total_cost_display')
    list_filter = ('house_class', 'report__year')
    search_fields = ('description',)
    raw_id_fields = ('report',)
    
    def total_cost_display(self, obj):
        return obj.total_cost
    total_cost_display.short_description = 'Total Cost'
    total_cost_display.admin_order_field = 'old_cost'

@admin.register(OfficeBuilding)
class OfficeBuildingAdmin(admin.ModelAdmin):
    list_display = ('office_name', 'office_class', 'date_built', 'old_cost',
                   'add_this_year', 'sub_this_year', 'total_cost_display')
    list_filter = ('office_class', 'report__year')
    search_fields = ('office_name',)
    raw_id_fields = ('report',)
    
    def total_cost_display(self, obj):
        return obj.total_cost
    total_cost_display.short_description = 'Total Cost'
    total_cost_display.admin_order_field = 'old_cost'

@admin.register(OtherBuilding)
class OtherBuildingAdmin(admin.ModelAdmin):
    list_display = ('building_name', 'building_class', 'date_built', 'old_cost',
                   'add_this_year', 'sub_this_year', 'total_cost_display')
    list_filter = ('building_class', 'report__year')
    search_fields = ('building_name',)
    raw_id_fields = ('report',)
    
    def total_cost_display(self, obj):
        return obj.total_cost
    total_cost_display.short_description = 'Total Cost'
    # Note: Can't order by property directly
    
    # Make form show readonly total cost
    readonly_fields = ('total_cost_display',)

@admin.register(Page1Summary)
class Page1SummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_chapels', 'total_pastoral', 'total_offices',
                   'total_other_buildings', 'grand_total', 'computed_at')
    list_filter = ('report__year',)
    search_fields = ('report__local__name', 'report__local__lcode')
    raw_id_fields = ('report',)
    readonly_fields = ('computed_at',)

# ====================
# PAGE 2 - ITEMS
# ====================
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'kaukulan', 'qty', 'unit_price', 'amount', 'date_received')
    list_filter = ('kaukulan', 'report__year')
    search_fields = ('item_name', 'iin_code', 'brand', 'model', 'serial_number')
    raw_id_fields = ('report',)

@admin.register(ItemsSummary)
class ItemsSummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_amount')
    raw_id_fields = ('report',)
    readonly_fields = ('total_amount',)

# ====================
# PAGE 3 - ITEMS ADDED
# ====================
@admin.register(ItemAdded)
class ItemAddedAdmin(admin.ModelAdmin):
    list_display = ('iin_code', 'kaukulan', 'qty', 'unit_price', 'amount', 'approval_number')
    list_filter = ('kaukulan', 'report__year')
    search_fields = ('iin_code', 'brand', 'serial_number', 'approval_number')
    raw_id_fields = ('report',)

@admin.register(ItemAddedSummary)
class ItemAddedSummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_amount')
    raw_id_fields = ('report',)
    readonly_fields = ('total_amount',)

# ====================
# PAGE 4 - ITEMS REMOVED
# ====================
@admin.register(ItemRemoved)
class ItemRemovedAdmin(admin.ModelAdmin):
    list_display = ('iin_code', 'source_place', 'qty', 'unit_price', 'amount', 'reason')
    list_filter = ('source_place', 'report__year')
    search_fields = ('iin_code', 'source_place', 'reason', 'approval_number')
    raw_id_fields = ('report',)

@admin.register(ItemRemovedSummary)
class ItemRemovedSummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_amount')
    raw_id_fields = ('report',)
    readonly_fields = ('total_amount',)

# ====================
# PAGE 5 - LAND, PLANTS, VEHICLES
# ====================
@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ('address', 'area_sqm', 'date_acquired', 'value', 'category', 'building_on_land')
    list_filter = ('category', 'report__year')
    search_fields = ('address', 'building_on_land', 'remarks')
    raw_id_fields = ('report',)

@admin.register(LandSummary)
class LandSummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_value', 'no_land_type', 'owner', 'contract_amount')
    raw_id_fields = ('report',)

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'plant_type', 'last_year_qty', 'this_year_qty', 'total_value_current')
    list_filter = ('plant_type', 'report__year')
    search_fields = ('name',)
    raw_id_fields = ('report',)

@admin.register(PlantSummary)
class PlantSummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_value')
    raw_id_fields = ('report',)
    readonly_fields = ('total_value',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make_type', 'plate_number', 'year_model', 'cost', 'category', 'assigned_user')
    list_filter = ('category', 'report__year')
    search_fields = ('make_type', 'plate_number', 'assigned_user', 'designation')
    raw_id_fields = ('report',)

@admin.register(VehicleSummary)
class VehicleSummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_value')
    raw_id_fields = ('report',)
    readonly_fields = ('total_value',)

# ====================
# REPORT SUMMARY
# ====================
@admin.register(ReportSummary)
class ReportSummaryAdmin(admin.ModelAdmin):
    list_display = ('report', 'p1_total', 'p2_total', 'p3_total', 'p4_total', 
                   'p5_total', 'total_summary')
    list_filter = ('report__year',)
    search_fields = ('report__local__name', 'report__local__lcode')
    raw_id_fields = ('report',)
    readonly_fields = ('p1_total', 'p2_total', 'p3_total', 'p4_total', 
                      'p5_total', 'total_summary')


