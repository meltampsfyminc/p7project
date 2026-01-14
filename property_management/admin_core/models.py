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
        editable=False,
        db_column="employee_id"
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
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

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
