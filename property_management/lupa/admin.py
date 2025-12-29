from django.contrib import admin
from .models import Land

@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ['local', 'location', 'lot_area', 'title_number', 'status','use_classification']
    list_filter = ['status', 'lot_type', 'local__district', 'use_classification']
    search_fields = ['local__name', 'location', 'title_number', 'owner']
    ordering = ['local', 'location']
    
    fieldsets = (
        ('Location Info', {
            'fields': ('local', 'location')
        }),
        ('Land Details', {
            'fields': ('lot_area', 'lot_type', 'use_classification')
        }),
        ('Ownership', {
            'fields': ('owner', 'title_number', 'status')
        }),
        ('Valuation', {
            'fields': ('market_value', 'acquisition_cost')
        }),
        ('Other', {
            'fields': ('remarks',)
        })
    )
