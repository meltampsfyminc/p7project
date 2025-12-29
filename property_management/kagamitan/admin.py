from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'quantity', 'local', 'location', 'date_acquired', 
                   'unit_price', 'total_price', 'year_reported', 'is_new']
    list_filter = ['location', 'year_reported', 'is_new', 'local__district']
    search_fields = ['item_name', 'brand', 'model', 'local__name', 'local__lcode', 'property_number']
    ordering = ['local', 'location', 'item_name']
    
    fieldsets = (
        ('Location & ID', {
            'fields': ('local', 'location', 'property_number')
        }),
        ('Item Details', {
            'fields': ('item_name', 'quantity', 'date_acquired', 'brand', 'model')
        }),
        ('Description', {
            'fields': ('material', 'color', 'size')
        }),
        ('Financial', {
            'fields': ('unit_price', 'total_price', 'reference_number')
        }),
        ('Reporting', {
            'fields': ('year_reported', 'is_new', 'remarks')
        }),
    )
    
    readonly_fields = ['total_price']
