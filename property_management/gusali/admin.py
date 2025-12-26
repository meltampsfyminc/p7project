from django.contrib import admin
from .models import Building, BuildingYearlyRecord


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'classification', 'current_total_cost', 'is_donated', 'local', 'year_covered']
    list_filter = ['code', 'is_donated', 'local', 'year_covered']
    search_fields = ['name', 'code', 'classification']
    ordering = ['code', 'name']
    
    fieldsets = (
        ('Building Information', {
            'fields': ('code', 'name', 'classification', 'local')
        }),
        ('Donation Status', {
            'fields': ('is_donated', 'donation_date')
        }),
        ('Ownership', {
            'fields': ('ownership_date', 'constructor', 'capacity')
        }),
        ('Financial', {
            'fields': ('original_cost', 'current_total_cost', 'year_covered')
        }),
        ('Notes', {
            'fields': ('remarks',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BuildingYearlyRecord)
class BuildingYearlyRecordAdmin(admin.ModelAdmin):
    list_display = ['building', 'year', 'cost_last_year', 'total_added', 'broken_removed_cost', 'year_end_total']
    list_filter = ['year', 'building__code']
    search_fields = ['building__name']
    ordering = ['-year', 'building__code']
    
    fieldsets = (
        ('Building & Year', {
            'fields': ('building', 'year')
        }),
        ('Beginning of Year', {
            'fields': ('cost_last_year',)
        }),
        ('Additions', {
            'fields': ('construction_cost', 'renovation_cost', 'general_repair_cost', 'other_additions_cost', 'total_added')
        }),
        ('Removed/Broken', {
            'fields': ('broken_removed_part', 'broken_removed_cost')
        }),
        ('End of Year', {
            'fields': ('year_end_total', 'remarks')
        }),
    )
    
    readonly_fields = ['total_added', 'year_end_total']
