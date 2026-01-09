from django.conf import settings
from django.db import models
from django.utils import timezone


# --------------------------------------------------
# Property
# --------------------------------------------------

class Property(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('sold', 'Sold'),
        ('maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    property_type = models.CharField(max_length=100)
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.IntegerField(blank=True, null=True)
    square_feet = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# --------------------------------------------------
# Housing Unit
# --------------------------------------------------

class HousingUnit(models.Model):
    occupant_name = models.CharField(
        max_length=255,
        help_text='Name of occupant/unit head'
    )
    department = models.CharField(max_length=255)
    section = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    date_reported = models.DateField(
        help_text='Date of report (Petsa ng Pag-uulat)'
    )
    housing_unit_name = models.CharField(
        max_length=100,
        help_text='e.g., Unit 22'
    )
    building = models.CharField(
        max_length=100,
        help_text='e.g., Abra'
    )
    floor = models.CharField(
        max_length=50,
        blank=True,
        help_text='Floor number'
    )
    unit_number = models.CharField(
        max_length=100,
        blank=True
    )
    address = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # NOTE: property FK added later in codebase usage
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='housing_units'
    )

    class Meta:
        verbose_name = 'Housing Unit'
        verbose_name_plural = 'Housing Units'
        ordering = ['-date_reported']

    def __str__(self):
        return f"{self.housing_unit_name} - {self.occupant_name}"


# --------------------------------------------------
# Property Inventory
# --------------------------------------------------

class PropertyInventory(models.Model):
    housing_unit = models.ForeignKey(
        HousingUnit,
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )

    item_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='IIN (Item Identification Number)'
    )
    item_name = models.CharField(
        max_length=255,
        help_text='Name of item (e.g., Sofa bed)'
    )
    brand = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    make = models.CharField(
        max_length=255,
        blank=True,
        help_text='Material composition'
    )
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(
        max_length=100,
        blank=True,
        help_text='Size/Dimension'
    )
    serial_number = models.CharField(max_length=255, blank=True)

    date_acquired = models.DateField(
        help_text='Date when item was acquired'
    )
    quantity = models.IntegerField(default=1)

    # Accounting / depreciation fields
    acquisition_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        help_text='Original acquisition cost'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        help_text='Total value (acquisition_cost × quantity)'
    )
    useful_life = models.IntegerField(
        default=5,
        help_text='Useful life in years'
    )
    net_book_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        help_text='Current net book value after depreciation'
    )

    remarks = models.TextField(
        blank=True,
        help_text="e.g., 'fr. Bodega-maayos'"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Property Inventory'
        verbose_name_plural = 'Property Inventory'
        ordering = ['housing_unit', 'item_name']
        indexes = [
            models.Index(fields=['housing_unit', 'item_name'])
        ]

    def __str__(self):
        return f"{self.item_name} ({self.housing_unit})"


# --------------------------------------------------
# Imported File
# --------------------------------------------------

class ImportedFile(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('error', 'Error'),
    ]

    filename = models.CharField(max_length=500)
    file_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text='SHA256 hash of file'
    )
    file_size = models.BigIntegerField(
        help_text='File size in bytes'
    )
    imported_at = models.DateTimeField(auto_now_add=True)
    records_imported = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success'
    )
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Imported File'
        verbose_name_plural = 'Imported Files'
        ordering = ['-imported_at']

    def __str__(self):
        return self.filename


# --------------------------------------------------
# User Profile (2FA)
# --------------------------------------------------

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    is_2fa_enabled = models.BooleanField(
        default=False,
        help_text='Is 2FA enabled for this user'
    )
    totp_secret = models.CharField(
        max_length=32,
        blank=True,
        help_text='TOTP secret key'
    )
    backup_codes = models.TextField(
        blank=True,
        help_text='Comma-separated backup codes'
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    last_login_date = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile: {self.user}"


# --------------------------------------------------
# Backup Codes
# --------------------------------------------------

class BackupCode(models.Model):
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='backup_codes_list'
    )
    code = models.CharField(
        max_length=20,
        help_text='Backup code (8 hex characters)'
    )
    is_used = models.BooleanField(
        default=False,
        help_text='Has this code been used?'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When was this code used?'
    )
    expires_at = models.DateTimeField(
        help_text='When does this code expire?'
    )

    class Meta:
        verbose_name = 'Backup Code'
        verbose_name_plural = 'Backup Codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_profile', 'code']),
            models.Index(fields=['user_profile', 'is_used', 'expires_at']),
        ]

    def __str__(self):
        return f"BackupCode({self.user_profile.user})"


# --------------------------------------------------
# Item Transfer
# --------------------------------------------------

class ItemTransfer(models.Model):
    TRANSFER_TYPE_CHOICES = [
        ('unit_to_unit', 'Unit to Unit'),
        ('unit_to_storage', 'Unit to Storage (Bodega)'),
        ('storage_to_unit', 'Storage to Unit'),
        ('return', 'Return'),
        ('scrap', 'Scrap/Disposal'),
    ]

    STATUS_CHOICES = [
        ('good', 'Good Condition'),
        ('damaged', 'Damaged'),
        ('broken', 'Broken'),
        ('lost', 'Lost'),
    ]

    inventory_item = models.ForeignKey(
        PropertyInventory,
        on_delete=models.CASCADE,
        related_name='transfers'
    )
    from_unit = models.ForeignKey(
        HousingUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_transferred_from'
    )
    to_unit = models.ForeignKey(
        HousingUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_transferred_to'
    )

    transfer_type = models.CharField(
        max_length=20,
        choices=TRANSFER_TYPE_CHOICES,
        default='unit_to_unit'
    )
    to_storage = models.BooleanField(
        default=False,
        help_text='Is item transferred to storage/bodega?'
    )
    transferred_by = models.CharField(
        max_length=255,
        help_text='Name of person who gave/transferred the item'
    )
    receiver_name = models.CharField(
        max_length=255,
        help_text='Name of person who received the item'
    )
    transfer_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Date of transfer'
    )
    received_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date when item was received'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='good'
    )
    reason = models.TextField(
        help_text='Reason for transfer/pullout'
    )
    remarks = models.TextField(
        blank=True,
        help_text='Additional remarks or notes'
    )
    quantity = models.IntegerField(
        default=1,
        help_text='Quantity of items transferred'
    )

    # Scrap / disposal
    is_scrapped = models.BooleanField(
        default=False,
        help_text='Is this item being scrapped/disposed?'
    )
    scrap_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when item was scrapped/disposed'
    )
    scrap_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text='Reason for scrapping'
    )
    scrap_sell_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        help_text='Sell value if scrapped'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Item Transfer'
        verbose_name_plural = 'Item Transfers'
        ordering = ['-transfer_date']
        indexes = [
            models.Index(fields=['transfer_date', 'status']),
            models.Index(fields=['inventory_item', 'transfer_date']),
        ]

    def __str__(self):
        return f"Transfer #{self.id}"
