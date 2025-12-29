from django.db import models
from decimal import Decimal

class Land(models.Model):
    """
    Land (Lupa) Model
    Based on P7 Annual Report Page 5A
    """
    CLASSIFICATION_CHOICES = [
        ('TITULADO', 'Titulado'),
        ('TAX_DEC', 'Tax Declaration'),
        ('OTHER', 'Other'),
    ]
    
    # Relationship to Local
    local = models.ForeignKey(
        'properties.Local',
        on_delete=models.CASCADE,
        related_name='lands',
        null=True,
        blank=True,
        help_text="Local where land is located"
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
    
    # Column 1: Location
    location = models.CharField(
        max_length=255,
        help_text="Lokasyon"
    )
    
    # Column 2: Area
    lot_area = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Sukat (sqm)"
    )
    
    # Column 3: Kind
    lot_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Uri ng Lupa (Res/Com/Agri/Inst)"
    )
    
    # Column 4: Title No
    title_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="TCT/OCT Number"
    )
    
    # Column 5: Owner
    owner = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nagmamay-ari"
    )
    
    # Column 6: Status
    status = models.CharField(
        max_length=50,
        choices=CLASSIFICATION_CHOICES,
        default='TITULADO',
        help_text="Kaurian (Titulado/Tax Dec)"
    )
    
    # Column 7-8: Value
    market_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Market Value"
    )
    
    acquisition_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Acquisition Cost"
    )
    
    # Column 9: Use
    use_classification = models.CharField(
        max_length=100,
        blank=True,
        help_text="Gamit (e.g., Kapilya, Pastoral)"
    )
    
    remarks = models.TextField(
        blank=True,
        help_text="Remarks"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['local', 'location']
        verbose_name = 'Land (Lupa)'
        verbose_name_plural = 'Lands (Lupa)'
        
    def __str__(self):
        return f"{self.local} - {self.location} ({self.lot_area} sqm)"
