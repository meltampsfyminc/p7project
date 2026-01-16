from django.contrib import admin
from .models import (Pamayanan, HousingUnit, HousingUnitInventory, ImportedFile, UserProfile, ItemTransfer, 
                     District, Local, DistrictProperty, DistrictInventory, LocalProperty, LocalInventory)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_2fa_enabled', 'timezone', 'currency', 'last_login_date', 'created_at')
    list_filter = ('is_2fa_enabled', 'timezone', 'currency', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('2FA Settings', {
            'fields': ('is_2fa_enabled', 'totp_secret', 'backup_codes')
        }),
        ('User Preferences', {
            'fields': ('timezone', 'currency')
        }),
        ('Login Information', {
            'fields': ('last_login_ip', 'last_login_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImportedFile)
class ImportedFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'file_size', 'records_imported', 'status', 'imported_at')
    list_filter = ('status', 'imported_at')
    search_fields = ('filename', 'file_hash')
    readonly_fields = ('file_hash', 'imported_at')


@admin.register(Pamayanan)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'property_type', 'total_units', 'status', 'created_at')
    list_filter = ('status', 'property_type', 'owner', 'created_at')
    search_fields = ('name', 'address', 'city', 'owner')
    readonly_fields = ('created_at', 'updated_at', 'get_unit_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner', 'property_type')
        }),
        ('Location', {
            'fields': ('address', 'city', 'province', 'postal_code')
        }),
        ('Property Details', {
            'fields': ('total_units', 'get_unit_count')
        }),
        ('Financial Information', {
            'fields': ('acquisition_cost', 'current_value')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )




@admin.register(HousingUnitInventory)
class PropertyInventoryAdmin(admin.ModelAdmin):
    list_display = ('housing_unit', 'item_name', 'quantity', 'date_acquired', 'color', 'size', 'remarks')
    list_filter = ('housing_unit', 'date_acquired', 'created_at')
    search_fields = ('item_name', 'brand', 'model', 'housing_unit__housing_unit_name', 'housing_unit__occupant_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Item Identification', {
            'fields': ('housing_unit', 'item_code', 'item_name', 'date_acquired')
        }),
        ('Quantity', {
            'fields': ('quantity',)
        }),
        ('Description', {
            'fields': ('brand', 'model', 'make', 'color', 'size', 'serial_number')
        }),
        ('Additional Information', {
            'fields': ('remarks',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemTransfer)
class ItemTransferAdmin(admin.ModelAdmin):
    list_display = ('inventory_item', 'get_source', 'get_destination', 'receiver_name', 'status', 'transfer_date')
    list_filter = ('transfer_type', 'status', 'transfer_date', 'to_storage')
    search_fields = ('inventory_item__item_name', 'receiver_name', 'transferred_by', 'reason')
    readonly_fields = ('transfer_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Item Information', {
            'fields': ('inventory_item',)
        }),
        ('Transfer Details', {
            'fields': ('transfer_type', 'from_unit', 'to_unit', 'to_storage', 'quantity')
        }),
        ('Personnel Information', {
            'fields': ('transferred_by', 'receiver_name')
        }),
        ('Transfer Information', {
            'fields': ('reason', 'remarks', 'status')
        }),
        ('Timestamps', {
            'fields': ('transfer_date', 'received_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('dcode', 'name', 'get_local_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('dcode', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'get_local_count')
    
    fieldsets = (
        ('District Information', {
            'fields': ('dcode', 'name')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Statistics', {
            'fields': ('get_local_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_local_count(self, obj):
        """Display the number of locals in this district"""
        return obj.locals.count()
    get_local_count.short_description = 'Number of Locals'


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ('lcode', 'name', 'district', 'created_at')
    list_filter = ('district', 'created_at')
    search_fields = ('lcode', 'name', 'description', 'district__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Local Information', {
            'fields': ('lcode', 'name', 'district')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DistrictProperty)
class DistrictPropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'property_type', 'status', 'acquisition_cost', 'current_value')
    list_filter = ('district', 'property_type', 'status', 'created_at')
    search_fields = ('name', 'address', 'city', 'district__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('district', 'name', 'property_type', 'description')
        }),
        ('Location', {
            'fields': ('address', 'city')
        }),
        ('Financial Information', {
            'fields': ('acquisition_cost', 'current_value')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DistrictInventory)
class DistrictInventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'property', 'quantity', 'date_acquired', 'brand', 'color', 'size')
    list_filter = ('property', 'date_acquired', 'created_at')
    search_fields = ('item_name', 'item_code', 'brand', 'model', 'property__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Item Identification', {
            'fields': ('property', 'item_code', 'item_name', 'date_acquired')
        }),
        ('Quantity', {
            'fields': ('quantity',)
        }),
        ('Description', {
            'fields': ('description', 'brand', 'model', 'make', 'color', 'size', 'serial_number')
        }),
        ('Additional Information', {
            'fields': ('remarks',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LocalProperty)
class LocalPropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'local', 'property_type', 'status', 'acquisition_cost', 'current_value')
    list_filter = ('local', 'local__district', 'property_type', 'status', 'created_at')
    search_fields = ('name', 'address', 'city', 'local__name', 'local__district__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('local', 'name', 'property_type', 'description')
        }),
        ('Location', {
            'fields': ('address', 'city')
        }),
        ('Financial Information', {
            'fields': ('acquisition_cost', 'current_value')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LocalInventory)
class LocalInventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'property', 'quantity', 'date_acquired', 'brand', 'color', 'size')
    list_filter = ('property', 'property__local__district', 'date_acquired', 'created_at')
    search_fields = ('item_name', 'item_code', 'brand', 'model', 'property__name', 'property__local__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Item Identification', {
            'fields': ('property', 'item_code', 'item_name', 'date_acquired')
        }),
        ('Quantity', {
            'fields': ('quantity',)
        }),
        ('Description', {
            'fields': ('description', 'brand', 'model', 'make', 'color', 'size', 'serial_number')
        }),
        ('Additional Information', {
            'fields': ('remarks',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
from django.contrib import admin
from .models import HousingUnit


@admin.register(HousingUnit)
class HousingUnitAdmin(admin.ModelAdmin):
    list_display = (
        "display_location",
        "unit_number",
        "occupant_name",
        "department",
        "section",
        "date_reported",
    )

    list_filter = (
        "pamayanan",
        "building",
        "department",
        "section",
        "date_reported",
    )

    search_fields = (
        "unit_number",
        "occupant_name",
        "pamayanan__name",
        "building__name",
    )

    ordering = (
        "pamayanan__name",
        "building__name",
        "unit_number",
    )

    @admin.display(description="Location")
    def display_location(self, obj):
        parts = [obj.pamayanan.name]
        if obj.building:
            parts.append(obj.building.name)
        return " → ".join(parts)
