from django.db import models

class Plant(models.Model):
    """
    Plant (Pananim) Model
    Based on P7 Annual Report Page 5B
    """
    # Relationship to Local
    local = models.ForeignKey(
        'properties.Local',
        on_delete=models.CASCADE,
        related_name='plants',
        null=True,
        blank=True,
        help_text="Local where plant is located"
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
    
    # Column 1: Name
    name = models.CharField(
        max_length=255,
        help_text="Pangalan ng Pananim (e.g., Mangga)"
    )
    
    # Column 2: Variety
    variety = models.CharField(
        max_length=100,
        blank=True,
        help_text="Uri (e.g., Piko, Indian)"
    )
    
    # Column 3: Fruit Bearing
    fruit_bearing = models.IntegerField(
        default=0,
        help_text="Nagbubunga"
    )
    
    # Column 4: Non-Fruit Bearing
    non_fruit_bearing = models.IntegerField(
        default=0,
        help_text="Hindi Nagbubunga"
    )
    
    # Column 5: Total
    total_quantity = models.IntegerField(
        default=0,
        help_text="Kabuuang Bilang"
    )
    
    # Value columns (Unit Price per seedling? Or total value?)
    # Excel showed "Halaga ng Bawat Puno" and "Kabuuang Halaga"
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Halaga ng Bawat Puno"
    )
    
    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Kabuuang Halaga"
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Lokasyon (Brgy/Bayan)"
    )
    
    remarks = models.TextField(
        blank=True,
        help_text="Remarks"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['local', 'name']
        verbose_name = 'Plant (Pananim)'
        verbose_name_plural = 'Plants (Pananim)'
        
    def __str__(self):
        return f"{self.name} ({self.variety}) - {self.local}"
    
    def save(self, *args, **kwargs):
        self.total_quantity = self.fruit_bearing + self.non_fruit_bearing
        # If total value is not set but unit price is, calculate? 
        # Or depend on what's provided. Often best to calc if feasible.
        if self.unit_price and self.total_quantity:
            self.total_value = self.unit_price * self.total_quantity
        super().save(*args, **kwargs)
