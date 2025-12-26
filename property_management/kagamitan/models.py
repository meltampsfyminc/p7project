from django.db import models
from decimal import Decimal


class LocalEquipment(models.Model):
    """Equipment/Kagamitan inventory for a Local
    
    Represents equipment items tracked in the P7 Annual Report.
    Page 2 (II-A): Existing items from previous years
    Page 3 (II-B): Newly added items this year
    """
    
    LOCATION_CHOICES = [
        ('KAPILYA', 'Kapilya'),
        ('KORO', 'Koro'),
        ('OPISINA', 'Opisina'),
        ('IMBAKAN', 'Imbakan'),
        ('IBA', 'Iba'),
    ]
    
    # Relationship to Local (from properties app)
    local = models.ForeignKey(
        'properties.Local',
        on_delete=models.CASCADE,
        related_name='equipment',
        null=True,
        blank=True,
        help_text="Local where equipment is located"
    )
    
    # Location within the local
    location = models.CharField(
        max_length=50,
        choices=LOCATION_CHOICES,
        default='KAPILYA',
        help_text="Location within local (Kapilya, Koro, etc.)"
    )
    
    # Item identification
    item_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Item code (e.g., 01-001-02)"
    )
    
    # Item details
    year_acquired = models.IntegerField(
        help_text="Year the item was acquired"
    )
    quantity = models.IntegerField(
        default=1,
        help_text="Number of items"
    )
    item_name = models.CharField(
        max_length=255,
        help_text="Item description (e.g., Benches, Speaker)"
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        help_text="Brand name"
    )
    model_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model number"
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        help_text="Material type (e.g., Wooden, Metal)"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color"
    )
    size = models.CharField(
        max_length=50,
        blank=True,
        help_text="Size (e.g., 90x4.00m, 10\")"
    )
    
    # Financial information
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Price per unit (PHP)"
    )
    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total price (PHP)"
    )
    
    # Report tracking
    year_reported = models.IntegerField(
        help_text="Year this was reported"
    )
    is_new_addition = models.BooleanField(
        default=False,
        help_text="True if from Page 3 (newly added this year)"
    )
    
    # Additional information
    remarks = models.TextField(
        blank=True,
        help_text="Remarks (e.g., Maayos po, Sira)"
    )
    p10_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="P-10 approval number (for new items)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['local', 'location', 'item_name']
        verbose_name = 'Local Equipment'
        verbose_name_plural = 'Local Equipment'
        indexes = [
            models.Index(fields=['local', 'year_reported']),
            models.Index(fields=['local', 'location']),
            models.Index(fields=['year_reported', 'is_new_addition']),
        ]
    
    def __str__(self):
        return f"{self.item_name} ({self.quantity}x) - {self.local.name if self.local else 'Unassigned'}"
    
    def calculate_total(self):
        """Calculate total price from quantity and unit price"""
        return Decimal(str(self.quantity)) * (self.unit_price or Decimal('0'))
    
    def save(self, *args, **kwargs):
        """Auto-calculate total price before saving"""
        if self.unit_price and self.quantity:
            self.total_price = self.calculate_total()
        super().save(*args, **kwargs)
