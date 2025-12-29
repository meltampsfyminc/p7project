from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
import hashlib
import pyotp
import secrets


class UserProfile(models.Model):
    """Extended user profile for 2FA and additional settings"""
    
    TIMEZONE_CHOICES = [
        ('PHT', 'Philippine Time (UTC+08:00)'),
        ('EST', 'Eastern Standard Time (UTC-05:00)'),
        ('UTC', 'Coordinated Universal Time (UTC±00:00)'),
        ('CET', 'Central European Time (UTC+01:00)'),
    ]
    
    CURRENCY_CHOICES = [
        ('PHP', 'Philippine Peso (₱)'),
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 2FA Settings
    is_2fa_enabled = models.BooleanField(default=False, help_text="Is 2FA enabled for this user")
    totp_secret = models.CharField(max_length=32, blank=True, help_text="TOTP secret key")
    backup_codes = models.TextField(blank=True, help_text="Comma-separated backup codes")
    
    # Timezone and Currency Settings
    timezone = models.CharField(
        max_length=10,
        choices=TIMEZONE_CHOICES,
        default='PHT',
        help_text="User's preferred timezone for datetime display"
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PHP',
        help_text="User's preferred currency for financial displays"
    )
    
    # Additional Settings
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    def generate_totp_secret(self):
        """Generate a new TOTP secret"""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self, issuer_name="Property Management"):
        """Get the provisioning URI for QR code generation"""
        if not self.totp_secret:
            self.generate_totp_secret()
        totp = pyotp.TOTP(self.totp_secret)
        return totp.provisioning_uri(
            name=self.user.email or self.user.username,
            issuer_name=issuer_name
        )
    
    def verify_totp(self, token):
        """Verify a TOTP token"""
        if not self.totp_secret:
            return False
        
        # Strip whitespace from token
        token = str(token).strip().replace(' ', '')
        
        # Validate token is numeric and 6 digits
        if not token.isdigit() or len(token) != 6:
            return False
        
        totp = pyotp.TOTP(self.totp_secret)
        # Allow for time skew (current, previous, and next time step for better UX)
        return totp.verify(token, valid_window=2)
    
    def generate_backup_codes(self, count=10, expire_hours=24):
        """Generate backup codes for 2FA with expiration time
        
        Args:
            count: Number of backup codes to generate
            expire_hours: Hours until codes expire (default 24 hours)
        
        Returns:
            List of generated backup codes
        """
        # Delete old backup codes for this user
        BackupCode.objects.filter(user_profile=self).delete()
        
        codes = []
        expiration_time = now() + timedelta(hours=expire_hours)
        
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            BackupCode.objects.create(
                user_profile=self,
                code=code,
                expires_at=expiration_time
            )
            codes.append(code)
        
        return codes
    
    def use_backup_code(self, code):
        """Use a backup code if valid and not expired
        
        Args:
            code: The backup code to validate
        
        Returns:
            True if code was valid and not expired, False otherwise
        """
        # Strip whitespace and convert to uppercase
        code = str(code).strip().upper()
        
        try:
            backup_code = BackupCode.objects.get(
                user_profile=self,
                code=code,
                is_used=False
            )
            
            # Check if code is expired
            if backup_code.is_expired():
                backup_code.delete()
                return False
            
            # Mark as used
            backup_code.is_used = True
            backup_code.used_at = now()
            backup_code.save()
            return True
            
        except BackupCode.DoesNotExist:
            return False
    
    def has_unused_backup_codes(self):
        """Check if user has unused, non-expired backup codes"""
        return BackupCode.objects.filter(
            user_profile=self,
            is_used=False,
            expires_at__gt=now()
        ).exists()


class BackupCode(models.Model):
    """Model to store backup codes with expiration time"""
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='backup_codes_list')
    code = models.CharField(max_length=20, help_text="Backup code (8 hex characters)")
    is_used = models.BooleanField(default=False, help_text="Has this code been used?")
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True, help_text="When was this code used?")
    expires_at = models.DateTimeField(help_text="When does this code expire?")
    
    class Meta:
        verbose_name = 'Backup Code'
        verbose_name_plural = 'Backup Codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_profile', 'code']),
            models.Index(fields=['user_profile', 'is_used', 'expires_at']),
        ]
    
    def __str__(self):
        status = "Used" if self.is_used else "Valid"
        return f"{self.code} ({status})"
    
    def is_expired(self):
        """Check if the code has expired"""
        return now() > self.expires_at
    
    def time_until_expiration(self):
        """Get time remaining until code expires"""
        if self.is_expired():
            return None
        return self.expires_at - now()


class ImportedFile(models.Model):
    """Track imported files to prevent duplicate imports"""
    
    filename = models.CharField(max_length=500)
    file_hash = models.CharField(max_length=64, unique=True, help_text="SHA256 hash of file")
    file_size = models.BigIntegerField(help_text="File size in bytes")
    imported_at = models.DateTimeField(auto_now_add=True)
    records_imported = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('partial', 'Partial'),
            ('error', 'Error'),
        ],
        default='success'
    )
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-imported_at']
        verbose_name = 'Imported File'
        verbose_name_plural = 'Imported Files'
    
    def __str__(self):
        return f"{self.filename} ({self.records_imported} records)"


class Property(models.Model):
    """Model for property/building management.
    
    Represents a physical building or property asset.
    Example: 'Abra Building' owned by the church
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('sold', 'Sold'),
    ]
    
    # Building/Property Information
    name = models.CharField(
        max_length=255,
        help_text="Building name (e.g., 'Abra Building')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the property/building"
    )
    
    # Address Information
    address = models.CharField(
        max_length=500,
        help_text="Street address"
    )
    city = models.CharField(
        max_length=100,
        help_text="City/Municipality"
    )
    province = models.CharField(
        max_length=100,
        blank=True,
        help_text="Province/State"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True
    )
    
    # Property Details
    property_type = models.CharField(
        max_length=100,
        help_text="Type of property (e.g., 'Building', 'Residential', 'Commercial')"
    )
    owner = models.CharField(
        max_length=255,
        help_text="Property owner (e.g., 'The Church')"
    )
    total_units = models.IntegerField(
        default=0,
        help_text="Total number of housing units in this property"
    )
    
    # Financial Information
    acquisition_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Property acquisition cost (PHP)"
    )
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current estimated property value (PHP)"
    )
    
    # Status and Timestamps
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property/Building'
        verbose_name_plural = 'Properties/Buildings'
    
    def __str__(self):
        return f"{self.name} ({self.owner})"
    
    def get_unit_count(self):
        """Get count of active housing units in this property"""
        return self.housing_units.count()


class HousingUnit(models.Model):
    """Model for housing unit information.
    
    Represents individual units within a Property/Building.
    Example: Unit 101 in 'Abra Building'
    """
    
    # Link to Property/Building
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='housing_units',
        null=True,
        blank=True,
        help_text="The building/property this unit belongs to"
    )
    
    # Unit Information
    unit_number = models.CharField(
        max_length=100,
        help_text="Unit number/identifier (e.g., '101', '102', 'Unit A')"
    )
    floor = models.CharField(
        max_length=50,
        blank=True,
        help_text="Floor number/level"
    )
    housing_unit_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Display name (e.g., 'Room 101')"
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        help_text="Full address of the unit"
    )
    
    # Occupant Information
    occupant_name = models.CharField(
        max_length=255,
        help_text="Name of occupant/unit head"
    )
    department = models.CharField(
        max_length=255,
        blank=True,
        help_text="Department of occupant"
    )
    section = models.CharField(
        max_length=255,
        blank=True,
        help_text="Section/Team of occupant"
    )
    job_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Job title of occupant"
    )
    
    # Dates
    date_reported = models.DateField(
        help_text="Date of report (Petsa ng Pag-uulat)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_reported']
        verbose_name = 'Housing Unit'
        verbose_name_plural = 'Housing Units'
    
    def __str__(self):
        if self.property:
            return f"{self.property.name} - Unit {self.unit_number} ({self.occupant_name})"
        return f"Unit {self.unit_number} - {self.occupant_name}"
    
    def save(self, *args, **kwargs):
        """Auto-generate housing_unit_name if not provided"""
        if not self.housing_unit_name:
            self.housing_unit_name = f"Unit {self.unit_number}"
        
        if not self.address and self.property:
            self.address = self.property.address
        
        super().save(*args, **kwargs)


class PropertyInventory(models.Model):
    """Model for tracking inventory items within a housing unit."""
    
    housing_unit = models.ForeignKey(HousingUnit, on_delete=models.CASCADE, related_name='inventory_items')
    
    # Item Identification
    item_code = models.CharField(max_length=50, blank=True, null=True, help_text="IIN (Item Identification Number)")
    date_acquired = models.DateField(help_text="Date when item was acquired")
    
    # Item Details
    quantity = models.IntegerField(default=1)
    item_name = models.CharField(max_length=255, help_text="Name of item (e.g., Sofa bed)")
    
    # Description Fields
    brand = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    make = models.CharField(max_length=255, blank=True, help_text="Material composition")
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True, help_text="Size/Dimension")
    serial_number = models.CharField(max_length=255, blank=True)
    
    # Financial Fields
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Original acquisition cost (PHP)")
    useful_life = models.IntegerField(default=5, help_text="Useful life in years")
    net_book_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Current net book value after depreciation (PHP)")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total value in PHP (acquisition_cost × quantity)")
    
    remarks = models.TextField(blank=True, help_text="e.g., 'fr. Bodega-maayos'")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['housing_unit', 'item_name']
        verbose_name = 'Property Inventory'
        verbose_name_plural = 'Property Inventory'
        indexes = [
            models.Index(fields=['housing_unit', 'item_name']),
        ]
    
    def __str__(self):
        return f"{self.housing_unit.housing_unit_name} - {self.item_name} (Qty: {self.quantity})"
    
    def calculate_amount(self):
        """Calculate total amount (acquisition_cost × quantity)"""
        from decimal import Decimal
        return (self.acquisition_cost or Decimal('0.00')) * (self.quantity or 0)
    
    def calculate_depreciation(self):
        """Calculate depreciation and net book value using straight-line method
        
        Formula:
        - Annual Depreciation = Acquisition Cost / Useful Life
        - Net Book Value = Acquisition Cost - Annual Depreciation
        """
        from decimal import Decimal
        
        if not self.acquisition_cost or self.useful_life <= 0:
            return Decimal('0.00')
        
        # Annual depreciation (assuming no salvage value)
        annual_depreciation = self.acquisition_cost / self.useful_life
        
        # Net book value after one year of depreciation
        net_book_value = max(Decimal('0.00'), self.acquisition_cost - annual_depreciation)
        
        return net_book_value * (self.quantity or 1)
    
    def save(self, *args, **kwargs):
        """Auto-calculate amount and net_book_value before saving"""
        # Calculate amount: acquisition_cost × quantity
        self.amount = self.calculate_amount()
        
        # Calculate net book value with depreciation
        self.net_book_value = self.calculate_depreciation()
        
        super().save(*args, **kwargs)


class ItemTransfer(models.Model):
    """Model to track item transfers/pullouts between units and storage"""
    
    STATUS_CHOICES = [
        ('good', 'Good Condition'),
        ('damaged', 'Damaged'),
        ('broken', 'Broken'),
        ('lost', 'Lost'),
    ]
    
    TRANSFER_TYPE_CHOICES = [
        ('unit_to_unit', 'Unit to Unit'),
        ('unit_to_storage', 'Unit to Storage (Bodega)'),
        ('storage_to_unit', 'Storage to Unit'),
        ('return', 'Return'),
        ('scrap', 'Scrap/Disposal'),
    ]
    
    # Item Information
    inventory_item = models.ForeignKey(PropertyInventory, on_delete=models.CASCADE, related_name='transfers')
    
    # Transfer Details
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES, default='unit_to_unit')
    from_unit = models.ForeignKey(HousingUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_transferred_from')
    to_unit = models.ForeignKey(HousingUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_transferred_to')
    to_storage = models.BooleanField(default=False, help_text="Is item transferred to storage/bodega?")
    
    # Personnel Information
    transferred_by = models.CharField(max_length=255, help_text="Name of person who gave/transferred the item")
    receiver_name = models.CharField(max_length=255, help_text="Name of person who received the item")
    
    # Tracking Information
    transfer_date = models.DateTimeField(auto_now_add=True, help_text="Date of transfer")
    received_date = models.DateTimeField(null=True, blank=True, help_text="Date when item was received")
    
    # Item Status and Remarks
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='good')
    reason = models.TextField(help_text="Reason for transfer/pullout")
    remarks = models.TextField(blank=True, help_text="Additional remarks or notes")
    
    # Quantity transferred
    quantity = models.IntegerField(default=1, help_text="Quantity of items transferred")
    
    # Scrap/Disposal Fields (for items being scrapped or sold as scrap)
    is_scrapped = models.BooleanField(default=False, help_text="Is this item being scrapped/disposed?")
    scrap_sell_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Sell value if scrapped in PHP (overrides for accounting)")
    scrap_date = models.DateField(null=True, blank=True, help_text="Date when item was scrapped/disposed")
    scrap_reason = models.CharField(max_length=255, blank=True, help_text="Reason for scrapping (e.g., Beyond repair, Obsolete, No longer needed)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transfer_date']
        verbose_name = 'Item Transfer'
        verbose_name_plural = 'Item Transfers'
        indexes = [
            models.Index(fields=['transfer_date', 'status']),
            models.Index(fields=['inventory_item', 'transfer_date']),
        ]
    
    def __str__(self):
        if self.is_scrapped:
            destination = "Scrap/Disposal"
        elif self.to_storage:
            destination = "Storage/Bodega"
        elif self.to_unit:
            destination = self.to_unit.housing_unit_name
        else:
            destination = "Unknown"
        
        source = self.from_unit.housing_unit_name if self.from_unit else "Storage"
        return f"{self.inventory_item.item_name} ({source} → {destination}) - {self.transfer_date.strftime('%Y-%m-%d')}"
    
    def get_destination(self):
        """Get the destination of the transfer"""
        if self.is_scrapped:
            return "Scrap/Disposal"
        if self.to_storage:
            return "Storage/Bodega"
        return self.to_unit.housing_unit_name if self.to_unit else "Unknown"
    
    def get_source(self):
        """Get the source of the transfer"""
        return self.from_unit.housing_unit_name if self.from_unit else "Storage/Bodega"
    
    def calculate_loss_on_scrap(self):
        """Calculate loss on scrap (net book value - sell value)
        
        Returns:
            Loss amount (positive = loss, negative = gain)
        """
        from decimal import Decimal
        if not self.is_scrapped:
            return Decimal('0.00')
        
        # Get the net book value for transferred quantity
        nbv_per_unit = self.inventory_item.net_book_value / self.inventory_item.quantity if self.inventory_item.quantity > 0 else Decimal('0.00')
        total_nbv = nbv_per_unit * self.quantity
        
        # Sell value
        sell_value = self.scrap_sell_value or Decimal('0.00')
        
        # Loss = NBV - Sell Value
        return total_nbv - sell_value
    
    def mark_as_scrapped(self, sell_value=None, scrap_reason=None):
        """Mark item as scrapped and set scrap details
        
        Args:
            sell_value: The salvage/sell value of scrapped item
            scrap_reason: Reason for scrapping
        """
        from datetime import date
        self.is_scrapped = True
        self.transfer_type = 'scrap'
        self.to_storage = False  # Not going to storage if scrapped
        self.scrap_date = date.today()
        if sell_value is not None:
            self.scrap_sell_value = sell_value
        if scrap_reason:
            self.scrap_reason = scrap_reason
        self.save()


class District(models.Model):
    """Church District - similar to a county in America
    
    Represents a district in the Church of Christ (Iglesia Ni Cristo).
    A district contains multiple locals (cities).
    """
    dcode = models.CharField(
        max_length=10,
        unique=True,
        primary_key=True,
        help_text="District code (unique identifier)"
    )
    name = models.CharField(
        max_length=100,
        help_text="District name"
    )
    description = models.TextField(
        blank=True,
        help_text="District description"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'district'
        ordering = ['name']
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
    
    def __str__(self):
        return f"{self.name} ({self.dcode})"


class Local(models.Model):
    """Church Local - similar to a city in America within a county
    
    Represents a local (congregation/city) in the Church of Christ.
    Each local belongs to a district.
    """
    lcode = models.CharField(
        max_length=10,
        help_text="Local code (unique identifier)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Local name"
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='locals',
        help_text="District this local belongs to"
    )
    description = models.TextField(
        blank=True,
        help_text="Local description"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lokal'
        ordering = ['district', 'name']
        unique_together = ['lcode', 'district']
        verbose_name = 'Local'
        verbose_name_plural = 'Locals'
    
    def __str__(self):
        return f"{self.name} ({self.lcode}) - {self.district.name}"
    
    def get_district_code(self):
        """Get the district code for this local"""
        return self.district.dcode


class DistrictProperty(models.Model):
    """Property managed at District level
    
    Properties owned or managed by the district (e.g., district offices, meeting halls, etc.)
    """
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='properties',
        help_text="District that owns/manages this property"
    )
    name = models.CharField(
        max_length=200,
        help_text="Property name"
    )
    description = models.TextField(
        blank=True,
        help_text="Property description"
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Property address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City where property is located"
    )
    property_type = models.CharField(
        max_length=50,
        default='Building',
        help_text="Type of property (e.g., Building, Land, Office, Hall)"
    )
    acquisition_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Cost when property was acquired"
    )
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Current estimated value"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('maintenance', 'Under Maintenance'),
            ('sold', 'Sold'),
        ],
        default='active',
        help_text="Property status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['district', 'name']
        verbose_name = 'District Property'
        verbose_name_plural = 'District Properties'
    
    def __str__(self):
        return f"{self.name} - {self.district.name}"


class DistrictInventory(models.Model):
    """Items/Inventory in District Properties
    
    Tracks items owned by the district (e.g., equipment, furniture, etc.)
    """
    property = models.ForeignKey(
        DistrictProperty,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        help_text="Property where item is stored"
    )
    item_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unique item code"
    )
    item_name = models.CharField(
        max_length=200,
        help_text="Name of the item"
    )
    description = models.TextField(
        blank=True,
        help_text="Item description"
    )
    quantity = models.IntegerField(
        default=1,
        help_text="Quantity of item"
    )
    date_acquired = models.DateField(
        help_text="Date when item was acquired"
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        help_text="Brand/Manufacturer"
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model number"
    )
    make = models.CharField(
        max_length=100,
        blank=True,
        help_text="Make/Type"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color of item"
    )
    size = models.CharField(
        max_length=50,
        blank=True,
        help_text="Size of item"
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Serial number if applicable"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Additional remarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['property', 'item_name']
        verbose_name = 'District Inventory Item'
        verbose_name_plural = 'District Inventory Items'
    
    def __str__(self):
        return f"{self.item_name} ({self.quantity}x) - {self.property.name}"


class LocalProperty(models.Model):
    """Property managed at Local level
    
    Properties owned or managed by a local (e.g., local offices, meeting halls, etc.)
    """
    local = models.ForeignKey(
        Local,
        on_delete=models.CASCADE,
        related_name='properties',
        help_text="Local that owns/manages this property"
    )
    name = models.CharField(
        max_length=200,
        help_text="Property name"
    )
    description = models.TextField(
        blank=True,
        help_text="Property description"
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Property address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City where property is located"
    )
    property_type = models.CharField(
        max_length=50,
        default='Building',
        help_text="Type of property (e.g., Building, Land, Office, Hall)"
    )
    acquisition_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Cost when property was acquired"
    )
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Current estimated value"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('maintenance', 'Under Maintenance'),
            ('sold', 'Sold'),
        ],
        default='active',
        help_text="Property status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['local', 'name']
        verbose_name = 'Local Property'
        verbose_name_plural = 'Local Properties'
    
    def __str__(self):
        return f"{self.name} - {self.local.name}"


class LocalInventory(models.Model):
    """Items/Inventory in Local Properties
    
    Tracks items owned by the local (e.g., equipment, furniture, etc.)
    """
    property = models.ForeignKey(
        LocalProperty,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        help_text="Property where item is stored"
    )
    item_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unique item code"
    )
    item_name = models.CharField(
        max_length=200,
        help_text="Name of the item"
    )
    description = models.TextField(
        blank=True,
        help_text="Item description"
    )
    quantity = models.IntegerField(
        default=1,
        help_text="Quantity of item"
    )
    date_acquired = models.DateField(
        help_text="Date when item was acquired"
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        help_text="Brand/Manufacturer"
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model number"
    )
    make = models.CharField(
        max_length=100,
        blank=True,
        help_text="Make/Type"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color of item"
    )
    size = models.CharField(
        max_length=50,
        blank=True,
        help_text="Size of item"
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Serial number if applicable"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Additional remarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['property', 'item_name']
        verbose_name = 'Local Inventory Item'
        verbose_name_plural = 'Local Inventory Items'
    
    def __str__(self):
        return f"{self.item_name} ({self.quantity}x) - {self.property.name}"
