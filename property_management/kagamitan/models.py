from django.db import models
from decimal import Decimal


class Item(models.Model):
    """Kagamitan Item Model
    
    Represents an item record from P7 Annual Report (Page 2 and 3).
    Page 2 (II-A): Existing items
    Page 3 (II-B): Newly added items
    """
    
    # Relationship to Local
    local = models.ForeignKey(
        'properties.Local',
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
        blank=True,
        help_text="Local where item is located"
    )
    
    # Location codes
    dcode = models.CharField(
        max_length=10,
        blank=True,
        help_text="District code (DCODE)"
    )
    lcode = models.CharField(
        max_length=10,
        blank=True,
        help_text="Local code (LCODE)"
    )
    
    # Location within local (Column A)
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Location (e.g., Koro, Kalihiman)"
    )
    
    # Identification (Column B)
    property_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Property Number / Item Code"
    )
    
    # Acquisition (Column C)
    date_acquired = models.DateField(
        null=True,
        blank=True,
        help_text="Date acquired"
    )
    
    # Details (Column D-J)
    quantity = models.IntegerField(
        default=1,
        help_text="Quantity (Col D)"
    )
    item_name = models.CharField(
        max_length=255,
        help_text="Item Name/Description (Col E)"
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        help_text="Brand (Col F)"
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model (Col G)"
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        help_text="Material (Col H)"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color (Col I)"
    )
    size = models.CharField(
        max_length=50,
        blank=True,
        help_text="Size (Col J)"
    )
    
    # Financial (Column K-L)
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Unit Price (Col K)"
    )
    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total Price (Col L)"
    )
    
    # Additional (Column M+)
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference/Invoice Number (Col M)"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Remarks/Status"
    )
    
    # Report Context
    year_reported = models.IntegerField(
        help_text="Year reported"
    )
    is_new = models.BooleanField(
        default=False,
        help_text="True if new addition (Page 3)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['location', 'item_name']
        verbose_name = 'Item (Kagamitan)'
        verbose_name_plural = 'Items (Kagamitan)'
        indexes = [
            models.Index(fields=['local', 'year_reported']),
            models.Index(fields=['local', 'location']),
        ]
    
    def __str__(self):
        return f"{self.item_name} - {self.location}"
    
    def calculate_total(self):
        return Decimal(str(self.quantity)) * (self.unit_price or Decimal('0'))
    
    def save(self, *args, **kwargs):
        if self.unit_price and self.quantity:
            self.total_price = self.calculate_total()
        super().save(*args, **kwargs)
