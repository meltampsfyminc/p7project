from django.contrib import admin
from .models import (
    Department,
    Section,
    AdminBuilding,
    Office,
    Worker,
    WorkerOfficeAssignment,
    HousingUnitAssignment,
)

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

    inlines = [
        WorkerOfficeAssignmentInline,
        HousingUnitAssignmentInline,
    ]

    fieldsets = (
        ("Identity", {
            "fields": (
                "employee_no",
                ("first_name", "middle_name", "last_name"),
            )
        }),
        ("Classification", {
            "fields": (
                "category",
                "mwa_type",
                "marital_status",
                "employment_status",
            )
        }),
        ("Dates", {
            "fields": (
                "date_started",
                "date_ended",
            )
        }),
        ("Remarks", {
            "fields": ("remarks",),
        }),
    )


# ==========================
# D. ASSIGNMENTS (HISTORY)
# ==========================

@admin.register(WorkerOfficeAssignment)
class WorkerOfficeAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "worker",
        "office",
        "is_primary",
        "start_date",
        "end_date",
    )
    list_filter = ("is_primary", "office__building")
    search_fields = (
        "worker__last_name",
        "office__name",
        "office__building__name",
    )
    ordering = ("-start_date",)


@admin.register(HousingUnitAssignment)
class HousingUnitAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "worker",
        "housing_unit",
        "is_current",
        "start_date",
        "end_date",
    )
    list_filter = ("is_current",)
    search_fields = (
        "worker__last_name",
        "housing_unit__unit_number",
    )
    ordering = ("-start_date",)
