from django import forms
from django.forms import modelformset_factory

from .models import (
    AdminBuilding,
    Department,
    Section,
    Office,
    Worker,
    WorkerOfficeAssignment,
    HousingUnitAssignment,
)

# =====================================================
# 🏢 ADMIN BUILDINGS
# =====================================================

class AdminBuildingForm(forms.ModelForm):
    class Meta:
        model = AdminBuilding
        fields = ["name", "address"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = AdminBuilding.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Building name already exists.")
        return name


# =====================================================
# 🏛️ DEPARTMENTS
# =====================================================

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = Department.objects.exclude(pk=self.instance.pk).filter(
            name__iexact=name
        )
        if qs.exists():
            raise forms.ValidationError("Department name already exists.")
        return name


# =====================================================
# 🧩 SECTIONS
# =====================================================

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["department", "name"]

    def clean(self):
        cleaned = super().clean()
        department = cleaned.get("department")
        name = cleaned.get("name")

        if department and name:
            qs = Section.objects.exclude(pk=self.instance.pk).filter(
                department=department,
                name__iexact=name
            )
            if qs.exists():
                raise forms.ValidationError(
                    "This Section already exists in the selected Department."
                )
        return cleaned


# =====================================================
# 👤 WORKERS
# =====================================================

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            "employee_no",
            "first_name",
            "middle_name",
            "last_name",
            "category",
            "mwa_type",
            "marital_status",
            "employment_status",
            "date_started",
            "date_ended",
            "remarks",
        ]
        widgets = {
            "date_started": forms.DateInput(attrs={"type": "date"}),
            "date_ended": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        mwa_type = cleaned.get("mwa_type")
        marital_status = cleaned.get("marital_status")

        if category == "MWA" and not mwa_type:
            raise forms.ValidationError(
                "MWA workers must have a specific MWA type."
            )

        if category != "MWA" and mwa_type:
            raise forms.ValidationError(
                "Only MWA workers may have an MWA type."
            )

        if mwa_type == "student" and marital_status != "single":
            raise forms.ValidationError("Students must be single.")

        if mwa_type == "widow" and marital_status != "widowed":
            raise forms.ValidationError("Widow must be widowed.")

        return cleaned


# =====================================================
# 🏢 OFFICES
# =====================================================

class OfficeForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = ["building", "name", "department"]

    def clean(self):
        cleaned = super().clean()
        building = cleaned.get("building")
        name = cleaned.get("name")

        if building and name:
            qs = Office.objects.filter(
                building=building,
                name__iexact=name
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "An office with this name already exists in this building."
                )
        return cleaned


# =====================================================
# 🔁 WORKER ↔ OFFICE ASSIGNMENT
# =====================================================

class WorkerOfficeAssignmentForm(forms.ModelForm):
    class Meta:
        model = WorkerOfficeAssignment
        fields = [
            "worker",
            "office",
            "start_date",
            "end_date",
            "is_primary",
        ]

    def clean(self):
        cleaned = super().clean()
        worker = cleaned.get("worker")
        office = cleaned.get("office")
        is_primary = cleaned.get("is_primary")

        if worker and office:
            qs = WorkerOfficeAssignment.objects.exclude(pk=self.instance.pk).filter(
                worker=worker,
                office=office
            )
            if qs.exists():
                raise forms.ValidationError(
                    "This worker is already assigned to this office."
                )

        if is_primary and worker:
            qs = WorkerOfficeAssignment.objects.exclude(pk=self.instance.pk).filter(
                worker=worker,
                is_primary=True
            )
            if qs.exists():
                raise forms.ValidationError(
                    "A worker can only have one primary office."
                )

        return cleaned


# =====================================================
# 🏠 WORKER ↔ HOUSING ASSIGNMENT
# =====================================================

class HousingUnitAssignmentForm(forms.ModelForm):
    class Meta:
        model = HousingUnitAssignment
        fields = [
            "worker",
            "housing_unit",
            "start_date",
            "end_date",
            "remarks",
        ]

    def clean(self):
        cleaned = super().clean()
        worker = cleaned.get("worker")
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")

        if start and end and end < start:
            raise forms.ValidationError(
                "End date cannot be earlier than start date."
            )

        if worker:
            qs = HousingUnitAssignment.objects.exclude(pk=self.instance.pk).filter(
                worker=worker,
                end_date__isnull=True
            )
            if qs.exists():
                raise forms.ValidationError(
                    "This worker already has an active housing assignment."
                )

        return cleaned


# =====================================================
# 📋 MASS ENCODING FORMSETS
# =====================================================

DepartmentFormSet = modelformset_factory(
    Department, form=DepartmentForm, extra=5, can_delete=False
)

SectionFormSet = modelformset_factory(
    Section, form=SectionForm, extra=5, can_delete=False
)

OfficeFormSet = modelformset_factory(
    Office, form=OfficeForm, extra=5, can_delete=False
)

WorkerFormSet = modelformset_factory(
    Worker, form=WorkerForm, extra=3, can_delete=False
)
