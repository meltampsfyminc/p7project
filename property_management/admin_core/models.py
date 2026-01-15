import hashlib
from django.db import models
from django.utils import timezone


# ==========================
# A. DEPARTMENT & SECTION
# ==========================

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


# ==========================
# B. ADMIN BUILDINGS & OFFICES
# ==========================

class AdminBuilding(models.Model):
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


# ==========================
# C. WORKERS
# ==========================

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

    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        editable=False
    )

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

    identity_hash = models.CharField(
     max_length=64,
     unique=True,
     db_index=True,
     editable=False,
     blank=True      # TEMP
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

    date_started = models.DateField(default=timezone.now)
    date_ended = models.DateField(blank=True, null=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    # -------------------------
    # Identity Fingerprint
    # -------------------------
    def generate_identity_hash(self):
        """
        Generates a stable identity fingerprint for the worker.
        """
        raw = f"{self.first_name}|{self.middle_name}|{self.last_name}|{self.category}"
        raw = raw.strip().lower()
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def save(self, *args, **kwargs):
        if not self.identity_hash:
            self.identity_hash = self.generate_identity_hash()
        super().save(*args, **kwargs)

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        from django.core.exceptions import ValidationError

        if self.category == "MWA" and not self.mwa_type:
            raise ValidationError("MWA workers must have a specific MWA type.")

        if self.category != "MWA" and self.mwa_type:
            raise ValidationError("Only MWA workers may have an MWA type.")

        if self.mwa_type == "student" and self.marital_status != "single":
            raise ValidationError("Students must be single.")

        if self.mwa_type == "widow" and self.marital_status != "widowed":
            raise ValidationError("Widow must have marital status = Widowed.")
   
# ==========================
# D. ASSIGNMENTS
# ==========================

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


class HousingUnitAssignment(models.Model):
    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="housing_assignments"
    )
    housing_unit = models.ForeignKey(
        "properties.HousingUnit",
        on_delete=models.CASCADE,
        related_name="worker_assignments"
    )

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    is_current = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.worker} @ {self.housing_unit}"

class SyncConflict(models.Model):

    CONFLICT_TYPE_CHOICES = [
        ("WORKER_IDENTITY", "Worker Identity Conflict"),
        ("DEPARTMENT_MISMATCH", "Department Mismatch"),
        ("SECTION_MISMATCH", "Section Mismatch"),
        ("OFFICE_ASSIGNMENT", "Office Assignment Conflict"),
        ("HOUSING_ASSIGNMENT", "Housing Assignment Conflict"),
        ("BUILDING_MISMATCH", "Building Mismatch"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    # What kind of conflict
    conflict_type = models.CharField(
        max_length=50,
        choices=CONFLICT_TYPE_CHOICES
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default="medium"
    )

    # Who / what is affected
    worker = models.ForeignKey(
        "Worker",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conflicts"
    )

    identity_hash = models.CharField(
        max_length=64,
        db_index=True
    )

    # Snapshot of values
    existing_value = models.TextField()
    incoming_value = models.TextField()

    # Metadata
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
        indexes = [
            models.Index(fields=["conflict_type", "resolved"]),
            models.Index(fields=["identity_hash"]),
        ]

    def __str__(self):
        return f"{self.conflict_type} | {self.identity_hash[:8]} | {self.severity}"

class SyncRun(models.Model):
    """
    Immutable audit log for each sync execution.
    """

    STATUS_CHOICES = [
        ("success", "Success"),
        ("partial", "Partial (with conflicts)"),
        ("failed", "Failed"),
    ]

    source = models.CharField(
        max_length=100,
        default="properties_sync",
        help_text="Source system or trigger"
    )

    triggered_by = models.CharField(
        max_length=150,
        blank=True,
        help_text="Username, system, or scheduler"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="success"
    )

    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Counters
    departments_created = models.PositiveIntegerField(default=0)
    sections_created = models.PositiveIntegerField(default=0)
    workers_created = models.PositiveIntegerField(default=0)
    buildings_created = models.PositiveIntegerField(default=0)
    offices_created = models.PositiveIntegerField(default=0)
    assignments_created = models.PositiveIntegerField(default=0)

    conflicts_detected = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"SyncRun {self.id} | {self.status} | {self.started_at:%Y-%m-%d %H:%M}"

class ConflictFieldDecision(models.Model):
    conflict = models.ForeignKey(
        "SyncConflict",
        on_delete=models.CASCADE,
        related_name="field_decisions"
    )

    field_name = models.CharField(max_length=100)

    DECISION_CHOICES = [
        ("existing", "Keep Existing"),
        ("incoming", "Use Incoming"),
    ]

    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default="existing"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("conflict", "field_name")

    def __str__(self):
        return f"{self.field_name}: {self.decision}"
