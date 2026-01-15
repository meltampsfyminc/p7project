from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DepartmentFormSet, HousingUnitAssignmentForm, OfficeForm, OfficeFormSet, SectionFormSet, WorkerForm, WorkerFormSet, WorkerOfficeAssignmentForm
from .models import AdminBuilding, Department, HousingUnitAssignment, Office, Section, Worker, WorkerOfficeAssignment
from django.db.models import Count
from .models import Department
from .forms import DepartmentForm
from .models import Section
from .forms import SectionForm
from .models import AdminBuilding
from .forms import AdminBuildingForm


@login_required
def worker_bulk_create(request):
    queryset = Worker.objects.none()  # avoid loading existing workers

    if request.method == "POST":
        formset = WorkerFormSet(request.POST, queryset=queryset)

        if formset.is_valid():
            saved = 0
            for form in formset:
                if form.cleaned_data:
                    form.save()
                    saved += 1

            messages.success(
                request,
                f"{saved} worker(s) successfully saved."
            )
            return redirect("admin_core:worker_list")

        # ❗ IMPORTANT:
        # if invalid → data is preserved automatically

    else:
        formset = WorkerFormSet(queryset=queryset)

    return render(
        request,
        "admin_core/worker_bulk_form.html",
        {
            "formset": formset,
        }
    )
@login_required
def worker_list(request):
    workers = Worker.objects.select_related(
        "department",
        "section"
    ).order_by("last_name")

    return render(
        request,
        "admin_core/worker_list.html",
        {"workers": workers}
    )
    
@login_required
def admin_dashboard(request):
    context = {
        # Core counts
        "building_count": AdminBuilding.objects.count(),
        "department_count": Department.objects.count(),
        "section_count": Section.objects.count(),

        # Workers
        "worker_active": Worker.objects.filter(employment_status="active").count(),
        "worker_total": Worker.objects.count(),

        # Worker breakdown
        "worker_by_category": (
            Worker.objects.values("category")
            .annotate(total=Count("id"))
            .order_by("category")
        ),

        "mwa_breakdown": (
            Worker.objects.filter(category="MWA")
            .values("mwa_type")
            .annotate(total=Count("id"))
            .order_by("mwa_type")
        ),

        # Assignments
        "office_assignments": WorkerOfficeAssignment.objects.filter(
            end_date__isnull=True
        ).count(),

        "housing_assigned": HousingUnitAssignment.objects.filter(
            is_current=True
        ).count(),
    }

    return render(request, "admin_core/dashboard.html", context)




@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(
        request,
        "admin_core/department_list.html",
        {"departments": departments}
    )

@login_required
def department_create(request):
    form = DepartmentForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Department created successfully.")
        return redirect("admin_core:department_list")

    return render(
        request,
        "admin_core/department_form.html",
        {
            "form": form,
            "title": "Add Department",
        },
    )



@login_required
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if form.is_valid():
        form.save()
        return redirect("admin_core:department_list")

    return render(
        request,
        "admin_core/department_form.html",
        {"form": form, "title": "Edit Department"}
    )

@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted.")
        return redirect("admin_core:department_list")

    return render(
        request,
        "admin_core/confirm_delete.html",
        {
            "object": department,
            "type": "Department"
        }
    )

@login_required
def department_bulk_create(request):
    formset = DepartmentFormSet(
        request.POST or None,
        queryset=Department.objects.none()
    )

    if formset.is_valid():
        formset.save()
        messages.success(request, "Departments added successfully.")
        return redirect("admin_core:department_list")

    return render(
        request,
        "admin_core/department_bulk_form.html",
        {
            "formset": formset,
            "title": "Mass Add Departments"
        }
    )

@login_required
def admin_building_list(request):
    buildings = AdminBuilding.objects.all()
    return render(
        request,
        "admin_core/admin_building_list.html",
        {"buildings": buildings},
    )


@login_required
def office_list(request):
    offices = Office.objects.select_related(
        "building", "department"
    ).order_by("building__name", "name")

    buildings = AdminBuilding.objects.all()
    building_filter = request.GET.get("building")

    if building_filter:
        offices = offices.filter(building_id=building_filter)

    return render(
        request,
        "admin_core/office_list.html",
        {
            "offices": offices,
            "buildings": buildings,
            "building_filter": building_filter,
        },
    )


@login_required
def office_create(request):
    form = OfficeForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("admin_core:office_list")

    return render(
        request,
        "admin_core/office_form.html",
        {
            "form": form,
            "title": "Add Office",
        },
    )


@login_required
def office_update(request, pk):
    office = get_object_or_404(Office, pk=pk)
    form = OfficeForm(request.POST or None, instance=office)

    if form.is_valid():
        form.save()
        return redirect("admin_core:office_list")

    return render(
        request,
        "admin_core/office_form.html",
        {
            "form": form,
            "title": f"Edit Office – {office.name}",
        },
    )


@login_required
def worker_list(request):
    workers = Worker.objects.all()

    category = request.GET.get("category")
    status = request.GET.get("status")

    if category:
        workers = workers.filter(category=category)

    if status:
        workers = workers.filter(employment_status=status)

    workers = workers.order_by("last_name", "first_name")

    return render(
        request,
        "admin_core/worker_list.html",
        {
            "workers": workers,
            "category": category,
            "status": status,
        },
    )


@login_required
def worker_create(request):
    form = WorkerForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("admin_core:worker_list")

    return render(
        request,
        "admin_core/worker_form.html",
        {
            "form": form,
            "title": "Add Worker",
        },
    )


@login_required
def worker_update(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    form = WorkerForm(request.POST or None, instance=worker)

    if form.is_valid():
        form.save()
        return redirect("admin_core:worker_list")

    return render(
        request,
        "admin_core/worker_form.html",
        {
            "form": form,
            "title": f"Edit Worker – {worker}",
        },
    )


@login_required
def worker_detail(request, pk):
    worker = get_object_or_404(Worker, pk=pk)

    return render(
        request,
        "admin_core/worker_detail.html",
        {
            "worker": worker,
        },
    )

@login_required
def worker_office_list(request):
    assignments = (
        WorkerOfficeAssignment.objects
        .select_related("worker", "office", "office__building")
        .order_by("-is_primary", "-start_date")
    )

    return render(
        request,
        "admin_core/worker_office_list.html",
        {"assignments": assignments},
    )


@login_required
def worker_office_create(request):
    form = WorkerOfficeAssignmentForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("admin_core:worker_office_list")

    return render(
        request,
        "admin_core/worker_office_form.html",
        {"form": form, "title": "Assign Worker to Office"},
    )


@login_required
def worker_office_update(request, pk):
    assignment = get_object_or_404(WorkerOfficeAssignment, pk=pk)
    form = WorkerOfficeAssignmentForm(request.POST or None, instance=assignment)

    if form.is_valid():
        form.save()
        return redirect("admin_core:worker_office_list")

    return render(
        request,
        "admin_core/worker_office_form.html",
        {"form": form, "title": "Edit Office Assignment"},
    )


@login_required
def housing_assignment_list(request):
    assignments = (
        HousingUnitAssignment.objects
        .select_related("worker", "housing_unit", "housing_unit__property")
        .order_by("-is_current", "-start_date")
    )

    return render(
        request,
        "admin_core/housing_assignment_list.html",
        {"assignments": assignments},
    )


@login_required
def housing_assignment_create(request):
    form = HousingUnitAssignmentForm(request.POST or None)

    if form.is_valid():
        assignment = form.save(commit=False)

        # 🔒 Close any existing active assignment for this worker
        HousingUnitAssignment.objects.filter(
            worker=assignment.worker,
            is_current=True
        ).update(
            is_current=False,
            end_date=assignment.start_date
        )

        assignment.is_current = True
        assignment.save()

        return redirect("admin_core:housing_assignment_list")

    return render(
        request,
        "admin_core/housing_assignment_form.html",
        {"form": form, "title": "Assign Worker to Housing Unit"},
    )


@login_required
def housing_assignment_update(request, pk):
    assignment = get_object_or_404(HousingUnitAssignment, pk=pk)
    form = HousingUnitAssignmentForm(request.POST or None, instance=assignment)

    if form.is_valid():
        form.save()
        return redirect("admin_core:housing_assignment_list")

    return render(
        request,
        "admin_core/housing_assignment_form.html",
        {"form": form, "title": "Edit Housing Assignment"},
    )

@login_required
def mass_departments(request):
    FormSet = DepartmentFormSet

    if request.method == "POST":
        formset = FormSet(request.POST, queryset=Department.objects.none())
        if formset.is_valid():
            formset.save()
            return redirect("admin_core:mass_departments")
    else:
        formset = FormSet(queryset=Department.objects.none())

    return render(
        request,
        "admin_core/mass_departments.html",
        {"formset": formset},
    )
@login_required
def mass_sections(request):
    FormSet = SectionFormSet

    if request.method == "POST":
        formset = FormSet(request.POST, queryset=Section.objects.none())
        if formset.is_valid():
            formset.save()
            return redirect("admin_core:mass_sections")
    else:
        formset = FormSet(queryset=Section.objects.none())

    return render(
        request,
        "admin_core/mass_sections.html",
        {"formset": formset},
    )
@login_required
def mass_workers(request):
    FormSet = WorkerFormSet

    if request.method == "POST":
        formset = FormSet(request.POST, queryset=Worker.objects.none())
        if formset.is_valid():
            formset.save()
            return redirect("admin_core:mass_workers")
    else:
        formset = FormSet(queryset=Worker.objects.none())

    return render(
        request,
        "admin_core/mass_workers.html",
        {"formset": formset},
    )
@login_required
def mass_offices(request):
    FormSet = OfficeFormSet

    if request.method == "POST":
        formset = FormSet(request.POST, queryset=Office.objects.none())
        if formset.is_valid():
            formset.save()
            return redirect("admin_core:mass_offices")
    else:
        formset = FormSet(queryset=Office.objects.none())

    return render(
        request,
        "admin_core/mass_offices.html",
        {"formset": formset},
    )

from .models import Section
from .forms import SectionForm, SectionFormSet


@login_required
def section_list(request):
    sections = Section.objects.select_related("department")
    return render(
        request,
        "admin_core/section_list.html",
        {"sections": sections}
    )


@login_required
def section_create(request):
    form = SectionForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Section created successfully.")
        return redirect("admin_core:section_list")

    return render(
        request,
        "admin_core/section_form.html",
        {"form": form, "title": "Add Section"}
    )


@login_required
def section_update(request, pk):
    section = get_object_or_404(Section, pk=pk)
    form = SectionForm(request.POST or None, instance=section)

    if form.is_valid():
        form.save()
        messages.success(request, "Section updated successfully.")
        return redirect("admin_core:section_list")

    return render(
        request,
        "admin_core/section_form.html",
        {"form": form, "title": "Edit Section"}
    )


@login_required
def section_delete(request, pk):
    section = get_object_or_404(Section, pk=pk)

    if request.method == "POST":
        section.delete()
        messages.success(request, "Section deleted.")
        return redirect("admin_core:section_list")

    return render(
        request,
        "admin_core/confirm_delete.html",
        {
            "object": section,
            "type": "Section"
        }
    )


@login_required
def section_bulk_create(request):
    formset = SectionFormSet(
        request.POST or None,
        queryset=Section.objects.none()
    )

    if request.method == "POST" and formset.is_valid():
        formset.save()
        messages.success(request, "Sections added successfully.")
        return redirect("admin_core:section_list")

    return render(
        request,
        "admin_core/section_bulk_form.html",
        {
            "formset": formset,
            "title": "Mass Encode Sections"
        }
    )


@login_required
def admin_building_list(request):
    buildings = AdminBuilding.objects.all()
    return render(
        request,
        "admin_core/admin_building_list.html",
        {"buildings": buildings}
    )


@login_required
def admin_building_create(request):
    form = AdminBuildingForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Admin Building created.")
        return redirect("admin_core:admin_building_list")

    return render(
        request,
        "admin_core/admin_building_form.html",
        {"form": form, "title": "Add Admin Building"}
    )


@login_required
def admin_building_update(request, pk):
    building = get_object_or_404(AdminBuilding, pk=pk)
    form = AdminBuildingForm(request.POST or None, instance=building)

    if form.is_valid():
        form.save()
        messages.success(request, "Admin Building updated.")
        return redirect("admin_core:admin_building_list")

    return render(
        request,
        "admin_core/admin_building_form.html",
        {"form": form, "title": "Edit Admin Building"}
    )


@login_required
def admin_building_delete(request, pk):
    building = get_object_or_404(AdminBuilding, pk=pk)

    if request.method == "POST":
        building.delete()
        messages.success(request, "Admin Building deleted.")
        return redirect("admin_core:admin_building_list")

    return render(
        request,
        "admin_core/confirm_delete.html",
        {
            "object": building,
            "type": "Admin Building"
        }
    )


@login_required
def admin_building_bulk_create(request):
    BuildingFormSet = modelformset_factory(
        AdminBuilding,
        form=AdminBuildingForm,
        extra=5,
        can_delete=False
    )

    formset = BuildingFormSet(
        request.POST or None,
        queryset=AdminBuilding.objects.none()
    )

    if request.method == "POST" and formset.is_valid():
        formset.save()
        messages.success(request, "Admin Buildings added successfully.")
        return redirect("admin_core:admin_building_list")

    return render(
        request,
        "admin_core/admin_building_bulk_form.html",
        {
            "formset": formset,
            "title": "Mass Encode Admin Buildings"
        }
    )

# admin_core/views.py
@login_required
def office_assignment_bulk_create(request):
    title = "Mass Encode Office Assignments"

    AssignmentFormSet = modelformset_factory(
        WorkerOfficeAssignment,
        form=WorkerOfficeAssignmentForm,
        extra=5,
        can_delete=False
    )

    if request.method == "POST":
        formset = AssignmentFormSet(
            request.POST,
            queryset=WorkerOfficeAssignment.objects.none()
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Office assignments saved.")
            return redirect("admin_core:dashboard")
    else:
        formset = AssignmentFormSet(
            queryset=WorkerOfficeAssignment.objects.none()
        )

    return render(
        request,
        "admin_core/office_assignment_bulk_form.html",
        {
            "title": title,
            "formset": formset,
        }
    )

# ==========================
# SYNC CONFLICT MERGE VIEW
# ==========================

from django.contrib.admin.views.decorators import staff_member_required
from admin_core.models import SyncConflict, ConflictFieldDecision
from admin_core.services.conflict_resolver import ConflictResolver


@staff_member_required
def merge_conflict_view(request, conflict_id):
    conflict = get_object_or_404(SyncConflict, pk=conflict_id)

    fields = conflict.incoming_payload.keys()

    if request.method == "POST":
        merge_map = {}

        for field in fields:
            decision = request.POST.get(field)
            ConflictFieldDecision.objects.update_or_create(
                conflict=conflict,
                field_name=field,
                defaults={"decision": decision},
            )
            merge_map[field] = decision

        ConflictResolver.merge(conflict, request.user, merge_map)
        return redirect("admin:admin_core_syncconflict_changelist")

    return render(
        request,
        "admin_core/merge_conflict.html",
        {
            "conflict": conflict,
            "fields": fields,
            "existing": conflict.existing_snapshot,
            "incoming": conflict.incoming_payload,
        },
    )
