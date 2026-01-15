from django.contrib import admin
from django.urls import path, reverse

from admin_core.views import merge_conflict_view
from .models import (
    Department,
    Section,
    AdminBuilding,
    Office,
    SyncRun,
    Worker,
    WorkerOfficeAssignment,
    HousingUnitAssignment,
    SyncConflict,
    ConflictFieldDecision,
)

from django.utils.html import format_html

# ==========================
# A. DEPARTMENT & SECTION
# ==========================

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


# ==========================
# B. ADMIN BUILDINGS & OFFICES
# ==========================

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


# ==========================
# C. WORKERS
# ==========================

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


# ==========================
# D. ASSIGNMENTS
# ==========================

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

@admin.register(ConflictFieldDecision)
class ConflictFieldDecisionAdmin(admin.ModelAdmin):
    list_display = ("conflict", "field_name", "decision", "created_at")
    list_filter = ("decision",)
    search_fields = ("field_name",)


# ==========================
# E. SYNC CONFLICTS
# ==========================
@admin.register(SyncConflict)
class SyncConflictAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conflict_type",
        "severity",
        "identity_hash",
        "resolved",
        "created_at",
        "resolved_at",
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

    return format_html(
        '<a class="button" style="background:#417690;color:white;" href="merge/">Resolve</a>'
    )
    
# ==========================
# F. SYNC RUN AUDIT LOG
# ==========================
from django.contrib import admin
from django.utils.html import format_html
from .models import SyncRun



class SyncRunAdmin2(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "started_at",
        "finished_at",
        "duration_ms",
        "conflicts_detected",
        "conflict_link",
    )

    list_filter = (
        "status",
        "source",
        "started_at",
    )

    search_fields = (
        "id",
        "triggered_by",
        "notes",
    )

    ordering = ("-started_at",)

    readonly_fields = (
        "source",
        "triggered_by",
        "status",
        "started_at",
        "finished_at",
        "duration_ms",
        "departments_created",
        "sections_created",
        "workers_created",
        "buildings_created",
        "offices_created",
        "assignments_created",
        "conflicts_detected",
        "notes",
        "created_at",
    )

    fieldsets = (
        ("Sync Metadata", {
            "fields": (
                "source",
                "triggered_by",
                "status",
            )
        }),
        ("Timing", {
            "fields": (
                "started_at",
                "finished_at",
                "duration_ms",
            )
        }),
        ("Results Summary", {
            "fields": (
                "departments_created",
                "sections_created",
                "workers_created",
                "buildings_created",
                "offices_created",
                "assignments_created",
                "conflicts_detected",
            )
        }),
        ("Notes", {
            "fields": ("notes",),
        }),
    )

    # 🔗 CLICKABLE LINK TO CONFLICTS
    @admin.display(description="Conflicts")
    def conflict_link(self, obj):
        if obj.conflicts_detected == 0:
            return "—"
        url = (
            f"/admin/admin_core/syncconflict/"
            f"?sync_run__id__exact={obj.id}"
        )
        return format_html(
            '<a href="{}">View ({})</a>',
            url,
            obj.conflicts_detected
        )

    # 🔒 READ-ONLY ADMIN
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SyncRun)
class SyncRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "started_at",
        "finished_at",
        "duration_ms",
        "conflicts_detected",
        "conflicts_link",
    )

    list_filter = (
        "status",
        "source",
        "started_at",
    )

    search_fields = (
        "id",
        "triggered_by",
        "notes",
    )

    ordering = ("-started_at",)

    readonly_fields = (
        "source",
        "triggered_by",
        "status",
        "started_at",
        "finished_at",
        "duration_ms",
        "departments_created",
        "sections_created",
        "workers_created",
        "buildings_created",
        "offices_created",
        "assignments_created",
        "conflicts_detected",
        "notes",
        "created_at",
    )

    fieldsets = (
        ("Sync Metadata", {
            "fields": (
                "source",
                "triggered_by",
                "status",
            )
        }),
        ("Timing", {
            "fields": (
                "started_at",
                "finished_at",
                "duration_ms",
            )
        }),
        ("Results Summary", {
            "fields": (
                "departments_created",
                "sections_created",
                "workers_created",
                "buildings_created",
                "offices_created",
                "assignments_created",
                "conflicts_detected",
            )
        }),
        ("Notes", {
            "fields": ("notes",),
        }),
    )

    @admin.display(description="Conflicts")
    def conflicts_link(self, obj):
        if obj.conflicts_detected == 0:
            return "—"

        url = (
            "/admin/admin_core/syncconflict/"
            f"?sync_run__id__exact={obj.id}"
        )
        return f'<a href="{url}">View ({obj.conflicts_detected})</a>'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
