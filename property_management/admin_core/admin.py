from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html

from admin_core.views import merge_conflict_view
from .models import (
    Department,
    Section,
    AdminBuilding,
    Office,
    Worker,
    WorkerOfficeAssignment,
    HousingUnitAssignment,
    HousingSite,
    HousingBuilding,
    HousingUnit,
    SyncConflict,
    SyncRun,
)

# =====================================================
# A. DEPARTMENT & SECTION
# =====================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "created_at")
    list_filter = ("department",)
    search_fields = ("name", "department__name")
    ordering = ("department__name", "name")


# =====================================================
# B. ADMIN BUILDINGS & OFFICES
# =====================================================

class OfficeInline(admin.TabularInline):
    model = Office
    extra = 1
    show_change_link = True


@admin.register(AdminBuilding)
class AdminBuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "created_at")
    search_fields = ("name", "address")
    ordering = ("name",)
    inlines = [OfficeInline]


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "department", "created_at")
    list_filter = ("building", "department")
    search_fields = ("name", "building__name", "department__name")
    ordering = ("building__name", "name")


# =====================================================
# C. WORKERS
# =====================================================

class WorkerOfficeAssignmentInline(admin.TabularInline):
    model = WorkerOfficeAssignment
    extra = 1
    autocomplete_fields = ("office",)
    show_change_link = True


class HousingUnitAssignmentInline(admin.TabularInline):
    model = HousingUnitAssignment
    extra = 0
    autocomplete_fields = ("housing_unit",)
    show_change_link = True


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "category",
        "mwa_type",
        "employment_status",
        "marital_status",
    )
    list_filter = (
        "category",
        "mwa_type",
        "employment_status",
        "marital_status",
    )
    search_fields = (
        "first_name",
        "last_name",
        "employee_no",
    )
    ordering = ("last_name", "first_name")
    inlines = [WorkerOfficeAssignmentInline, HousingUnitAssignmentInline]


# =====================================================
# D. ASSIGNMENTS
# =====================================================

@admin.register(WorkerOfficeAssignment)
class WorkerOfficeAssignmentAdmin(admin.ModelAdmin):
    list_display = ("worker", "office", "is_primary", "start_date", "end_date")
    list_filter = ("is_primary", "office__building")
    ordering = ("-start_date",)


@admin.register(HousingUnitAssignment)
class HousingUnitAssignmentAdmin(admin.ModelAdmin):
    list_display = ("worker", "housing_unit", "is_current", "start_date", "end_date")
    list_filter = ("is_current",)
    ordering = ("-start_date",)


# =====================================================
# E. HOUSING (PAMAYANAN)
# =====================================================

@admin.register(HousingSite)
class HousingSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "is_multi_building", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(HousingBuilding)
class HousingBuildingAdmin(admin.ModelAdmin):
    list_display = ("site", "name", "created_at")
    list_filter = ("site",)
    search_fields = ("name", "site__name")
    ordering = ("site__name", "name")


@admin.register(HousingUnit)
class HousingUnitAdmin(admin.ModelAdmin):
    list_display = ("site", "building", "unit_label", "floor")
    list_filter = ("site", "building")
    search_fields = ("unit_label", "site__name", "building__name")
    ordering = ("site__name", "building__name", "unit_label")


# =====================================================
# F. SYNC CONFLICTS
# =====================================================

@admin.register(SyncConflict)
class SyncConflictAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conflict_type",
        "severity",
        "resolve_link",
        "identity_hash_short",
        "created_at",
    )

    list_filter = (
        "conflict_type",
        "severity",
        "resolved",
        "created_at",
    )

    search_fields = (
        "identity_hash",
        "existing_value",
        "incoming_value",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "conflict_type",
        "severity",
        "worker",
        "identity_hash",
        "existing_value",
        "incoming_value",
        "source",
        "resolved",
        "resolved_at",
        "created_at",
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:conflict_id>/merge/",
                self.admin_site.admin_view(merge_conflict_view),
                name="admin_core_syncconflict_merge",
            ),
        ]
        return custom_urls + urls

    @admin.display(description="Action")
    def resolve_link(self, obj):
        if obj.resolved:
            return format_html("<span style='color:green;'>✔ Resolved</span>")
        url = reverse("admin:admin_core_syncconflict_merge", args=[obj.id])
        return format_html('<a class="button" href="{}">Resolve</a>', url)

    @admin.display(description="Hash")
    def identity_hash_short(self, obj):
        return obj.identity_hash[:12] + "..." if obj.identity_hash else ""


# =====================================================
# G. SYNC RUN AUDIT LOG
# =====================================================

@admin.register(SyncRun)
class SyncRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "started_at",
        "finished_at",
        "duration_display",
        "conflicts_detected",
    )

    list_filter = (
        "status",
        "started_at",
    )

    search_fields = (
        "id",
        "notes",
    )

    ordering = ("-started_at",)

    readonly_fields = (
        "status",
        "started_at",
        "finished_at",
        "duration_display",
        "housing_sites_created",
        "housing_buildings_created",
        "housing_units_created",
        "workers_created",
        "conflicts_detected",
        "notes",
    )

    fieldsets = (
        ("Status", {
            "fields": ("status",),
        }),
        ("Timing", {
            "fields": (
                "started_at",
                "finished_at",
                "duration_display",
            )
        }),
        ("Results", {
            "fields": (
                "housing_sites_created",
                "housing_buildings_created",
                "housing_units_created",
                "workers_created",
                "conflicts_detected",
            )
        }),
        ("Notes", {
            "fields": ("notes",),
        }),
    )

    @admin.display(description="Duration")
    def duration_display(self, obj):
        if obj.finished_at and obj.started_at:
            delta = obj.finished_at - obj.started_at
            return f"{delta.total_seconds():.2f}s"
        return "—"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
