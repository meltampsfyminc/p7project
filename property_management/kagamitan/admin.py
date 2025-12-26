from django.contrib import admin
from .models import LocalEquipment


@admin.register(LocalEquipment)
class LocalEquipmentAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'quantity', 'local', 'location', 'year_acquired', 
                   'unit_price', 'total_price', 'year_reported', 'is_new_addition']
    list_filter = ['location', 'year_reported', 'is_new_addition', 'local__district']
    search_fields = ['item_name', 'brand', 'model_number', 'local__name', 'local__lcode']
    ordering = ['local', 'location', 'item_name']
    
    fieldsets = (
        ('Location', {
            'fields': ('local', 'location', 'item_code')
        }),
        ('Item Details', {
            'fields': ('item_name', 'quantity', 'year_acquired', 'brand', 'model_number')
        }),
        ('Description', {
            'fields': ('material', 'color', 'size')
        }),
        ('Financial', {
            'fields': ('unit_price', 'total_price')
        }),
        ('Reporting', {
            'fields': ('year_reported', 'is_new_addition', 'p10_number', 'remarks')
        }),
    )
    
    readonly_fields = ['total_price']
