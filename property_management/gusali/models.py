from django.db import models
from decimal import Decimal


class Building(models.Model):
    """Building/Gusali Report Model
    
    Represents a building record from GUSALI REPORT.xlsx format.
    Tracks building information, donation status, and current costs.
    """
    
    BUILDING_CODE_CHOICES = [
        ('A', 'A - Kapilya'),
        ('B', 'B - Pastoral/Caretaker'),
        ('C', 'C - Ministerial/Finance/Secretariat'),
        ('D', 'D - Other Buildings'),
    ]
    
    # Core identifiers
    code = models.CharField(
        max_length=5,
        choices=BUILDING_CODE_CHOICES,
        help_text="Building code (A, B, C, D)"
    )
    name = models.CharField(
        max_length=255,
        help_text="Building name (e.g., KAPILYA, GUARD HOUSE)"
    )
    classification = models.CharField(
        max_length=50,
        blank=True,
        help_text="Building classification (e.g., A-3, A-PH, ADL-1)"
    )
    
    # Donation information
    is_donated = models.BooleanField(
        default=False,
        help_text="Whether the building was donated (HANDOG)"
    )
    donation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when building was donated (PETSA INIHANDOG)"
    )
    
    # Ownership information
    ownership_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when building was acquired/owned (PETSA MAYARI)"
    )
    constructor = models.CharField(
        max_length=255,
        blank=True,
        help_text="Builder/Constructor (PAGAWA)"
    )
    capacity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Building capacity (number of people)"
    )
    
    # Financial information
    original_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Original cost of building (PHP)"
    )
    current_total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Current total cost including all additions (PHP)"
    )
    
    # Relationship to Local (from properties app)
    local = models.ForeignKey(
        'properties.Local',
        on_delete=models.CASCADE,
        related_name='gusali_buildings',
        null=True,
        blank=True,
        help_text="Local where building is located"
    )
    
    # Year covered for the report
    year_covered = models.IntegerField(
        default=2024,
        help_text="Year covered by the report"
    )
    
    # Additional information
    remarks = models.TextField(
        blank=True,
        help_text="Additional remarks or notes"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code', 'name']
        verbose_name = 'Building (Gusali)'
        verbose_name_plural = 'Buildings (Gusali)'
        indexes = [
            models.Index(fields=['code', 'local']),
            models.Index(fields=['local', 'year_covered']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_donation_status(self):
        """Get donation status text"""
        return "HANDOG" if self.is_donated else "HINDI HANDOG"
    
    def get_latest_yearly_record(self):
        """Get the most recent yearly record for this building"""
        return self.yearly_records.order_by('-year').first()


class BuildingYearlyRecord(models.Model):
    """Yearly cost record for a building
    
    Tracks annual cost changes including construction, renovation,
    repairs, and removed items.
    """
    
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='yearly_records',
        help_text="Building this record belongs to"
    )
    year = models.IntegerField(
        help_text="Year of this record"
    )
    
    # Beginning of year cost
    cost_last_year = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Cost from previous year (COST LAST YEAR)"
    )
    
    # Additions during the year
    construction_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Construction additions (CONSTRUCTION)"
    )
    renovation_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Renovation costs (RENOVATION)"
    )
    general_repair_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="General repair costs (GENERAL REPAIR)"
    )
    other_additions_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Other additions (OTHER)"
    )
    total_added = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total additions (calculated)"
    )
    
    # Removed during the year
    broken_removed_part = models.CharField(
        max_length=255,
        blank=True,
        help_text="Description of broken/removed parts (PART)"
    )
    broken_removed_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Cost of broken/removed items (COST)"
    )
    
    # End of year total
    year_end_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total cost at end of year (TOTAL)"
    )
    
    remarks = models.TextField(
        blank=True,
        help_text="Remarks for this year"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', 'building']
        verbose_name = 'Building Yearly Record'
        verbose_name_plural = 'Building Yearly Records'
        unique_together = ['building', 'year']
        indexes = [
            models.Index(fields=['building', 'year']),
        ]
    
    def __str__(self):
        return f"{self.building.name} - {self.year}"
    
    def calculate_total_added(self):
        """Calculate total additions for the year"""
        return (
            (self.construction_cost or Decimal('0')) +
            (self.renovation_cost or Decimal('0')) +
            (self.general_repair_cost or Decimal('0')) +
            (self.other_additions_cost or Decimal('0'))
        )
    
    def calculate_year_end_total(self):
        """Calculate year-end total: last year + additions - removals"""
        return (
            (self.cost_last_year or Decimal('0')) +
            self.calculate_total_added() -
            (self.broken_removed_cost or Decimal('0'))
        )
    
    def save(self, *args, **kwargs):
        """Auto-calculate totals before saving"""
        self.total_added = self.calculate_total_added()
        self.year_end_total = self.calculate_year_end_total()
        super().save(*args, **kwargs)
