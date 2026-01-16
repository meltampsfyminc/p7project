import hashlib
from django.db import models
from django.utils import timezone


# =====================================================
# A. DEPARTMENTS & SECTIONS (WORK STRUCTURE)
# =====================================================

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Section(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="sections"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("department", "name")
        ordering = ["department__name", "name"]

    def __str__(self):
        return f"{self.department.name} - {self.name}"


# =====================================================
# B. ADMIN BUILDINGS & OFFICES (WORK LOCATION)
# =====================================================

class AdminBuilding(models.Model):
    """
    Administrative / office buildings only
    (NOT housing / pamayanan)
    """
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Office(models.Model):
    building = models.ForeignKey(
        AdminBuilding,
        on_delete=models.CASCADE,
        related_name="offices"
    )
    name = models.CharField(max_length=200)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offices"
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("building", "name")
        ordering = ["building__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.building.name})"


# =====================================================
# C. WORKERS
# =====================================================

class Worker(models.Model):

    WORKER_CATEGORY_CHOICES = [
        ("MWA", "Ministry / Worker / Auxiliary"),
        ("VW", "Volunteer Worker"),
        ("CW", "Construction Worker"),
    ]

    MWA_TYPE_CHOICES = [
        ("minister", "Minister"),
        ("regular", "Regular Worker"),
        ("student", "Student"),
        ("retired", "Retired"),
        ("widow", "Widow"),
    ]

    MARITAL_STATUS_CHOICES = [
        ("single", "Single"),
        ("married", "Married"),
        ("widowed", "Widowed"),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("retired", "Retired"),
        ("terminated", "Terminated"),
    ]

    employee_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)

    category = models.CharField(max_length=3, choices=WORKER_CATEGORY_CHOICES)
    mwa_type = models.CharField(
        max_length=20,
        choices=MWA_TYPE_CHOICES,
        blank=True,
        null=True
    )

    marital_status = models.CharField(
        max_length=10,
        choices=MARITAL_STATUS_CHOICES,
        default="single"
    )

    employment_status = models.CharField(
        max_length=15,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="active"
    )

    identity_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        editable=False
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def generate_identity_hash(self):
        raw = f"{self.first_name}|{self.middle_name}|{self.last_name}|{self.category}"
        return hashlib.sha256(raw.lower().encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.identity_hash:
            self.identity_hash = self.generate_identity_hash()
        super().save(*args, **kwargs)


# =====================================================
# D. WORK ASSIGNMENTS
# =====================================================

class WorkerOfficeAssignment(models.Model):
    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="office_assignments"
    )
    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        related_name="worker_assignments"
    )

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.worker} → {self.office}"


# =====================================================
# E. HOUSING (PAMAYANAN)
# =====================================================

class HousingSite(models.Model):
    """
    Pamayanan / Housing compound
    Examples:
    - Abra
    - LIG Condo
    - High-rise Condo
    - Tagumpay Housing
    """

    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=300, blank=True)

    is_multi_building = models.BooleanField(
        default=False,
        help_text="Does this pamayanan have multiple buildings?"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HousingBuilding(models.Model):
    site = models.ForeignKey(
        HousingSite,
        on_delete=models.CASCADE,
        related_name="buildings"
    )

    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("site", "name")
        ordering = ["site__name", "name"]

    def __str__(self):
        return f"{self.site.name} - {self.name}"


class HousingUnit(models.Model):
    site = models.ForeignKey(
        HousingSite,
        on_delete=models.CASCADE,
        related_name="units"
    )

    building = models.ForeignKey(
        HousingBuilding,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="units"
    )

    unit_label = models.CharField(
        max_length=100,
        help_text="Unit identifier (11-03, Unit 22, House #5)"
    )

    floor = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["site__name", "building__name", "unit_label"]

    def __str__(self):
        parts = [self.site.name]
        if self.building:
            parts.append(self.building.name)
        parts.append(self.unit_label)
        return " → ".join(parts)


class HousingUnitAssignment(models.Model):
    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="housing_assignments"
    )

    housing_unit = models.ForeignKey(
        HousingUnit,
        on_delete=models.CASCADE,
        related_name="worker_assignments"
    )

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    is_current = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.worker} @ {self.housing_unit}"


# =====================================================
# F. SYNC & CONFLICT MANAGEMENT
# =====================================================

class SyncConflict(models.Model):

    CONFLICT_TYPE_CHOICES = [
        ("WORKER_IDENTITY", "Worker Identity Conflict"),
        ("DEPARTMENT_MISMATCH", "Department Mismatch"),
        ("SECTION_MISMATCH", "Section Mismatch"),
        ("ADMIN_BUILDING_MISMATCH", "Admin Building Mismatch"),
        ("HOUSING_SITE_MISMATCH", "Housing Site Mismatch"),
        ("HOUSING_BUILDING_MISMATCH", "Housing Building Mismatch"),
        ("HOUSING_ASSIGNMENT", "Housing Assignment Conflict"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    conflict_type = models.CharField(
        max_length=50,
        choices=CONFLICT_TYPE_CHOICES
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default="medium"
    )

    worker = models.ForeignKey(
        Worker,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conflicts"
    )

    identity_hash = models.CharField(max_length=64, db_index=True)
    existing_value = models.TextField()
    incoming_value = models.TextField()

    source = models.CharField(
        max_length=100,
        default="properties_sync"
    )

    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.conflict_type} | {self.identity_hash[:8]} | {self.severity}"


class SyncRun(models.Model):
    """
    Immutable audit log for each sync execution.
    """

    STATUS_CHOICES = [
        ("success", "Success"),
        ("partial", "Partial"),
        ("failed", "Failed"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="success"
    )

    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)

    housing_sites_created = models.PositiveIntegerField(default=0)
    housing_buildings_created = models.PositiveIntegerField(default=0)
    housing_units_created = models.PositiveIntegerField(default=0)
    workers_created = models.PositiveIntegerField(default=0)

    conflicts_detected = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"SyncRun {self.id} | {self.status}"
# admin_core/models.py (add this to the Sync & Conflict Management section)

class ConflictFieldDecision(models.Model):
    """
    Stores individual field-level decisions during conflict resolution
    """
    conflict = models.ForeignKey(
        SyncConflict,
        on_delete=models.CASCADE,
        related_name="field_decisions"
    )
    field_name = models.CharField(max_length=100)
    chosen_value = models.TextField()
    decision_type = models.CharField(
        max_length=20,
        choices=[
            ("keep_existing", "Keep Existing"),
            ("use_incoming", "Use Incoming"),
            ("manual_input", "Manual Input"),
        ]
    )
    resolved_by = models.CharField(max_length=100, blank=True)
    resolved_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.field_name} - {self.decision_type}"
