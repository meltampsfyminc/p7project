from django.contrib import admin
from .models import Plant

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['local', 'name', 'variety', 'fruit_bearing', 'non_fruit_bearing', 'total_quantity', 'total_value']
    list_filter = ['name', 'local__district']
    search_fields = ['local__name', 'name', 'variety', 'location']
    ordering = ['local', 'name']
    
    fieldsets = (
        ('Location Info', {
            'fields': ('local', 'location')
        }),
        ('Plant Details', {
            'fields': ('name', 'variety')
        }),
        ('Quantity', {
            'fields': ('fruit_bearing', 'non_fruit_bearing', 'total_quantity')
        }),
        ('Valuation', {
            'fields': ('unit_price', 'total_value')
        }),
        ('Other', {
            'fields': ('remarks',)
        })
    )
    
    readonly_fields = ['total_quantity', 'total_value']
