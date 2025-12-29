from django.db import models

class Vehicle(models.Model):
    """Vehicle Model
    
    Represents a vehicle record with location identification.
    """
    
    # Relationship to Local
    local = models.ForeignKey(
        'properties.Local',
        on_delete=models.CASCADE,
        related_name='vehicles',
        null=True,
        blank=True,
        help_text="Local where vehicle is assigned"
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
    
    # Vehicle Details
    item_name = models.CharField(
        max_length=255,
        help_text="General name/type (e.g., Passenger Van, Pickup)"
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        help_text="Brand/Make (e.g., Toyota, Mitsubishi)"
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model/Series (e.g., Hiace, L300)"
    )
    plate_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Plate Number"
    )
    conduction_sticker = models.CharField(
        max_length=20,
        blank=True,
        help_text="Conduction Sticker"
    )
    
    engine_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Engine Number"
    )
    chassis_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Chassis/V.I.N. Number"
    )
    
    year_model = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year Model"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color"
    )
    
    # Financial
    acquisition_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Acquisition Cost"
    )
    date_acquired = models.DateField(
        null=True,
        blank=True,
        help_text="Date acquired"
    )
    
    remarks = models.TextField(
        blank=True,
        help_text="Remarks/Status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['item_name', 'brand']
        verbose_name = 'Vehicle (Sasakyan)'
        verbose_name_plural = 'Vehicles (Sasakyan)'
        
    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number or 'No Plate'})"
