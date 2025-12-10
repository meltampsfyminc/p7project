from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now, timedelta
from decimal import Decimal
from datetime import date
import pyotp

from .models import UserProfile, Property, HousingUnit, PropertyInventory, ItemTransfer, BackupCode, ImportedFile


class UserProfileTests(TestCase):
    """Test UserProfile model and 2FA functionality"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
    
    def test_totp_secret_generation(self):
        """Test TOTP secret generation"""
        secret = self.profile.generate_totp_secret()
        self.assertIsNotNone(secret)
        self.assertEqual(len(secret), 32)
        self.assertEqual(self.profile.totp_secret, secret)
    
    def test_totp_verification_valid_code(self):
        """Test TOTP verification with valid code"""
        self.profile.generate_totp_secret()
        self.profile.save()
        
        totp = pyotp.TOTP(self.profile.totp_secret)
        valid_code = totp.now()
        
        result = self.profile.verify_totp(valid_code)
        self.assertTrue(result)
    
    def test_totp_verification_invalid_code(self):
        """Test TOTP verification with invalid code"""
        self.profile.generate_totp_secret()
        self.profile.save()
        
        result = self.profile.verify_totp('000000')
        self.assertFalse(result)
    
    def test_totp_verification_with_spaces(self):
        """Test TOTP verification handles spaces correctly"""
        self.profile.generate_totp_secret()
        self.profile.save()
        
        totp = pyotp.TOTP(self.profile.totp_secret)
        valid_code = totp.now()
        
        # Test with spaces
        code_with_spaces = f"{valid_code[:3]} {valid_code[3:]}"
        result = self.profile.verify_totp(code_with_spaces)
        self.assertTrue(result)
    
    def test_backup_code_generation(self):
        """Test backup code generation"""
        codes = self.profile.generate_backup_codes(5)
        
        self.assertEqual(len(codes), 5)
        self.assertEqual(BackupCode.objects.filter(user_profile=self.profile).count(), 5)
        
        for code in codes:
            backup = BackupCode.objects.get(user_profile=self.profile, code=code)
            self.assertFalse(backup.is_used)
    
    def test_backup_code_first_use(self):
        """Test using a backup code for the first time"""
        codes = self.profile.generate_backup_codes(3)
        first_code = codes[0]
        
        result = self.profile.use_backup_code(first_code)
        self.assertTrue(result)
        
        # Verify code is marked as used
        backup = BackupCode.objects.get(user_profile=self.profile, code=first_code)
        self.assertTrue(backup.is_used)
        self.assertIsNotNone(backup.used_at)
    
    def test_backup_code_cannot_be_reused(self):
        """Test that a used backup code cannot be reused"""
        codes = self.profile.generate_backup_codes(3)
        first_code = codes[0]
        
        # First use should succeed
        result1 = self.profile.use_backup_code(first_code)
        self.assertTrue(result1)
        
        # Second use should fail
        result2 = self.profile.use_backup_code(first_code)
        self.assertFalse(result2)
    
    def test_backup_code_case_insensitive(self):
        """Test that backup codes are case-insensitive"""
        codes = self.profile.generate_backup_codes(3)
        first_code = codes[0].lower()
        
        result = self.profile.use_backup_code(first_code)
        self.assertTrue(result)
    
    def test_backup_code_expiration(self):
        """Test backup code expiration"""
        # Create an expired backup code
        expired_code = BackupCode.objects.create(
            user_profile=self.profile,
            code='EXPIRED00',
            expires_at=now() - timedelta(hours=1)
        )
        
        result = self.profile.use_backup_code('EXPIRED00')
        self.assertFalse(result)
        
        # Verify expired code was deleted
        self.assertFalse(BackupCode.objects.filter(code='EXPIRED00').exists())
    
    def test_has_unused_backup_codes(self):
        """Test checking for unused backup codes"""
        self.profile.generate_backup_codes(5)
        self.assertTrue(self.profile.has_unused_backup_codes())
        
        # Use all codes
        for backup in BackupCode.objects.filter(user_profile=self.profile, is_used=False):
            backup.is_used = True
            backup.used_at = now()
            backup.save()
        
        self.assertFalse(self.profile.has_unused_backup_codes())


class AuthenticationTests(TestCase):
    """Test authentication and login flow"""
    
    def setUp(self):
        """Create test user and client"""
        self.user = User.objects.create_user(username='authtest', password='authpass123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client = Client()
    
    def test_login_without_2fa(self):
        """Test login without 2FA"""
        response = self.client.post('/properties/login/', {
            'username': 'authtest',
            'password': 'authpass123'
        }, follow=True)
        
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/properties/login/', {
            'username': 'authtest',
            'password': 'wrongpassword'
        })
        
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_with_2fa_shows_form(self):
        """Test that 2FA form is shown when 2FA is enabled"""
        # Enable 2FA
        self.profile.generate_totp_secret()
        self.profile.is_2fa_enabled = True
        self.profile.save()
        
        response = self.client.post('/properties/login/', {
            'username': 'authtest',
            'password': 'authpass123'
        })
        
        self.assertContains(response, '2FA Code')
        self.assertContains(response, 'totp_code')
    
    def test_authenticate_function(self):
        """Test Django authenticate function"""
        user = authenticate(username='authtest', password='authpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'authtest')
        
        # Test with wrong password
        user = authenticate(username='authtest', password='wrongpass')
        self.assertIsNone(user)


class PropertyInventoryTests(TestCase):
    """Test PropertyInventory model and depreciation calculation"""
    
    def setUp(self):
        """Create test housing unit"""
        self.property = Property.objects.create(
            name='Building A',
            owner='Test Owner',
            address='123 Test St',
            city='Test City',
            province='Test Province',
            postal_code='12345',
            property_type='residential',
            total_units=10,
            acquisition_cost=Decimal('100000.00'),
            current_value=Decimal('100000.00'),
            status='active'
        )
        
        self.unit = HousingUnit.objects.create(
            property=self.property,
            occupant_name='Test Occupant',
            department='Test Dept',
            section='Test Section',
            job_title='Tester',
            date_reported=date.today(),
            housing_unit_name='Unit 1',
            address='Test Address'
        )
    
    def test_amount_calculation(self):
        """Test amount calculation (acquisition_cost × quantity)"""
        item = PropertyInventory(
            housing_unit=self.unit,
            item_name='Test Item',
            quantity=3,
            acquisition_cost=Decimal('100.00'),
            useful_life=5,
            date_acquired=date.today()
        )
        item.save()
        
        expected_amount = Decimal('100.00') * 3
        self.assertEqual(item.amount, expected_amount)
    
    def test_net_book_value_calculation(self):
        """Test net book value calculation"""
        item = PropertyInventory(
            housing_unit=self.unit,
            item_name='Test Item',
            quantity=1,
            acquisition_cost=Decimal('1000.00'),
            useful_life=5,
            date_acquired=date.today()
        )
        item.save()
        
        # NBV = (Acquisition Cost - Annual Depreciation) × Quantity
        # Annual Depreciation = 1000 / 5 = 200
        # NBV = (1000 - 200) × 1 = 800
        expected_nbv = Decimal('800.00')
        self.assertEqual(item.net_book_value, expected_nbv)
    
    def test_net_book_value_with_quantity(self):
        """Test net book value calculation with quantity > 1"""
        item = PropertyInventory(
            housing_unit=self.unit,
            item_name='Test Item',
            quantity=2,
            acquisition_cost=Decimal('500.00'),
            useful_life=10,
            date_acquired=date.today()
        )
        item.save()
        
        # Annual Depreciation = 500 / 10 = 50
        # NBV per unit = 500 - 50 = 450
        # Total NBV = 450 × 2 = 900
        expected_nbv = Decimal('900.00')
        self.assertEqual(item.net_book_value, expected_nbv)
    
    def test_zero_acquisition_cost(self):
        """Test depreciation with zero acquisition cost"""
        item = PropertyInventory(
            housing_unit=self.unit,
            item_name='Test Item',
            quantity=1,
            acquisition_cost=Decimal('0.00'),
            useful_life=5,
            date_acquired=date.today()
        )
        item.save()
        
        self.assertEqual(item.amount, Decimal('0.00'))
        self.assertEqual(item.net_book_value, Decimal('0.00'))
    
    def test_auto_calculation_on_save(self):
        """Test that amount and net_book_value are auto-calculated on save"""
        item = PropertyInventory(
            housing_unit=self.unit,
            item_name='Test Item',
            quantity=5,
            acquisition_cost=Decimal('2000.00'),
            useful_life=8,
            date_acquired=date.today()
        )
        # Don't set amount and net_book_value manually
        item.save()
        
        # Verify they were auto-calculated
        expected_amount = Decimal('10000.00')
        expected_nbv = (Decimal('2000.00') - (Decimal('2000.00') / 8)) * 5
        
        self.assertEqual(item.amount, expected_amount)
        self.assertEqual(item.net_book_value, expected_nbv)
    
    def test_useful_life_variations(self):
        """Test depreciation with various useful life values"""
        test_cases = [
            (Decimal('1000.00'), 1, Decimal('0.00')),  # 1 year: NBV = 0
            (Decimal('1000.00'), 5, Decimal('800.00')),  # 5 years
            (Decimal('1000.00'), 10, Decimal('900.00')),  # 10 years
            (Decimal('500.00'), 2, Decimal('250.00')),  # 2 years
        ]
        
        for cost, life, expected_nbv in test_cases:
            item = PropertyInventory(
                housing_unit=self.unit,
                item_name=f'Item {life}yr',
                quantity=1,
                acquisition_cost=cost,
                useful_life=life,
                date_acquired=date.today()
            )
            item.save()
            self.assertEqual(item.net_book_value, expected_nbv)


class HousingUnitTests(TestCase):
    """Test HousingUnit model"""
    
    def setUp(self):
        """Create test property"""
        self.property = Property.objects.create(
            name='Tower A',
            owner='Test Owner',
            address='123 Main St',
            city='Test City',
            province='Test Province',
            postal_code='12345',
            property_type='residential',
            total_units=10,
            acquisition_cost=Decimal('100000.00'),
            current_value=Decimal('100000.00'),
            status='active'
        )
    
    def test_housing_unit_creation(self):
        """Test creating a housing unit"""
        unit = HousingUnit.objects.create(
            property=self.property,
            occupant_name='John Doe',
            department='Engineering',
            section='Software',
            job_title='Developer',
            date_reported=date.today(),
            housing_unit_name='Unit 101',
            address='123 Main St'
        )
        
        self.assertEqual(unit.occupant_name, 'John Doe')
        self.assertEqual(unit.housing_unit_name, 'Unit 101')
        # String representation should include property name
        self.assertEqual(str(unit), f"{self.property.name} - Unit {unit.unit_number} ({unit.occupant_name})")
    
    def test_housing_unit_with_inventory(self):
        """Test housing unit with inventory items"""
        unit = HousingUnit.objects.create(
            property=self.property,
            occupant_name='Jane Smith',
            department='HR',
            section='Admin',
            job_title='Manager',
            date_reported=date.today(),
            housing_unit_name='Unit 202',
            address='456 Oak Ave'
        )
        
        # Add inventory items
        item1 = PropertyInventory.objects.create(
            housing_unit=unit,
            item_name='Desk',
            quantity=1,
            acquisition_cost=Decimal('500.00'),
            useful_life=5,
            date_acquired=date.today()
        )
        
        item2 = PropertyInventory.objects.create(
            housing_unit=unit,
            item_name='Chair',
            quantity=2,
            acquisition_cost=Decimal('200.00'),
            useful_life=3,
            date_acquired=date.today()
        )
        
        self.assertEqual(unit.inventory_items.count(), 2)


class ItemTransferTests(TestCase):
    """Test ItemTransfer model"""
    
    def setUp(self):
        """Create test data"""
        self.property = Property.objects.create(
            name='Building 1',
            owner='Test Owner',
            address='Address 1',
            city='Test City',
            province='Test Province',
            postal_code='12345',
            property_type='residential',
            total_units=10,
            acquisition_cost=Decimal('100000.00'),
            current_value=Decimal('100000.00'),
            status='active'
        )
        
        self.unit1 = HousingUnit.objects.create(
            property=self.property,
            occupant_name='Occupant 1',
            department='Dept 1',
            section='Section 1',
            job_title='Job 1',
            date_reported=date.today(),
            housing_unit_name='Unit 1',
            address='Address 1'
        )
        
        self.unit2 = HousingUnit.objects.create(
            property=self.property,
            occupant_name='Occupant 2',
            department='Dept 2',
            section='Section 2',
            job_title='Job 2',
            date_reported=date.today(),
            housing_unit_name='Unit 2',
            address='Address 2'
        )
        
        self.item = PropertyInventory.objects.create(
            housing_unit=self.unit1,
            item_name='Test Item',
            quantity=5,
            acquisition_cost=Decimal('1000.00'),
            useful_life=5,
            date_acquired=date.today()
        )
    
    def test_unit_to_unit_transfer(self):
        """Test transferring item from one unit to another"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='unit_to_unit',
            from_unit=self.unit1,
            to_unit=self.unit2,
            transferred_by='Admin User',
            receiver_name='Occupant 2',
            status='good',
            reason='Reallocation',
            quantity=2
        )
        
        self.assertEqual(transfer.transfer_type, 'unit_to_unit')
        self.assertEqual(transfer.from_unit, self.unit1)
        self.assertEqual(transfer.to_unit, self.unit2)
        self.assertEqual(transfer.quantity, 2)
    
    def test_unit_to_storage_transfer(self):
        """Test transferring item to storage"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='unit_to_storage',
            from_unit=self.unit1,
            to_storage=True,
            transferred_by='Admin User',
            receiver_name='Storage Manager',
            status='good',
            reason='Temporary storage',
            quantity=3
        )
        
        self.assertEqual(transfer.transfer_type, 'unit_to_storage')
        self.assertTrue(transfer.to_storage)
        self.assertEqual(transfer.get_destination(), 'Storage/Bodega')
    
    def test_transfer_get_source(self):
        """Test getting transfer source"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='unit_to_unit',
            from_unit=self.unit1,
            to_unit=self.unit2,
            transferred_by='Admin User',
            receiver_name='Occupant 2',
            status='good',
            reason='Transfer',
            quantity=1
        )
        
        self.assertEqual(transfer.get_source(), 'Unit 1')
    
    def test_transfer_get_destination(self):
        """Test getting transfer destination"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='unit_to_unit',
            from_unit=self.unit1,
            to_unit=self.unit2,
            transferred_by='Admin User',
            receiver_name='Occupant 2',
            status='good',
            reason='Transfer',
            quantity=1
        )
        
        self.assertEqual(transfer.get_destination(), 'Unit 2')
    
    def test_scrap_transfer_creation(self):
        """Test creating a scrap/disposal transfer"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='scrap',
            from_unit=self.unit1,
            to_storage=False,
            transferred_by='Admin User',
            receiver_name='Scrap Manager',
            status='broken',
            reason='Item is broken and no longer usable',
            quantity=1,
            is_scrapped=True,
            scrap_sell_value=Decimal('50.00'),
            scrap_reason='Beyond repair'
        )
        
        self.assertTrue(transfer.is_scrapped)
        self.assertEqual(transfer.transfer_type, 'scrap')
        self.assertEqual(transfer.get_destination(), 'Scrap/Disposal')
        self.assertEqual(transfer.scrap_sell_value, Decimal('50.00'))
    
    def test_mark_as_scrapped_method(self):
        """Test mark_as_scrapped method"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='unit_to_storage',
            from_unit=self.unit1,
            to_storage=True,
            transferred_by='Admin User',
            receiver_name='Storage Manager',
            status='broken',
            reason='Temporary storage',
            quantity=2
        )
        
        # Mark as scrapped
        transfer.mark_as_scrapped(sell_value=Decimal('100.00'), scrap_reason='Beyond repair')
        
        self.assertTrue(transfer.is_scrapped)
        self.assertEqual(transfer.transfer_type, 'scrap')
        self.assertEqual(transfer.scrap_sell_value, Decimal('100.00'))
        self.assertEqual(transfer.scrap_reason, 'Beyond repair')
        self.assertFalse(transfer.to_storage)
    
    def test_calculate_loss_on_scrap(self):
        """Test calculating loss when item is scrapped"""
        # Item: $1000 cost, 5-year life, qty 1 = NBV $800
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='scrap',
            from_unit=self.unit1,
            to_storage=False,
            transferred_by='Admin User',
            receiver_name='Scrap Manager',
            status='broken',
            reason='Scrap',
            quantity=5,
            is_scrapped=True,
            scrap_sell_value=Decimal('200.00')
        )
        
        # NBV of item: $800 (per unit)
        # Total NBV for 5 units: $800 × 5 = $4000
        # Sell value: $200
        # Loss: $4000 - $200 = $3800
        loss = transfer.calculate_loss_on_scrap()
        expected_loss = Decimal('3800.00')
        self.assertEqual(loss, expected_loss)
    
    def test_calculate_gain_on_scrap(self):
        """Test calculating gain when scrapped for more than NBV"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='scrap',
            from_unit=self.unit1,
            to_storage=False,
            transferred_by='Admin User',
            receiver_name='Scrap Manager',
            status='good',
            reason='Sold as scrap',
            quantity=2,
            is_scrapped=True,
            scrap_sell_value=Decimal('2000.00')
        )
        
        # NBV of item: $800 (per unit)
        # Total NBV for 2 units: $800 × 2 = $1600
        # Sell value: $2000
        # Gain: $1600 - $2000 = -$400 (negative = gain)
        loss = transfer.calculate_loss_on_scrap()
        expected_gain = Decimal('-400.00')
        self.assertEqual(loss, expected_gain)
    
    def test_scrap_without_sell_value(self):
        """Test scrap transfer without sell value (complete loss)"""
        transfer = ItemTransfer.objects.create(
            inventory_item=self.item,
            transfer_type='scrap',
            from_unit=self.unit1,
            to_storage=False,
            transferred_by='Admin User',
            receiver_name='Scrap Manager',
            status='broken',
            reason='Disposal',
            quantity=3,
            is_scrapped=True
        )
        
        # NBV of item: $800 (per unit)
        # Total NBV for 3 units: $800 × 3 = $2400
        # Sell value: $0 (not set)
        # Loss: $2400 - $0 = $2400
        loss = transfer.calculate_loss_on_scrap()
        expected_loss = Decimal('2400.00')
        self.assertEqual(loss, expected_loss)


class BackupCodeTests(TestCase):
    """Test BackupCode model"""
    
    def setUp(self):
        """Create test user and backup code"""
        self.user = User.objects.create_user(username='backuptest', password='testpass')
        self.profile = UserProfile.objects.create(user=self.user)
    
    def test_backup_code_creation(self):
        """Test creating a backup code"""
        backup = BackupCode.objects.create(
            user_profile=self.profile,
            code='TESTCODE1',
            expires_at=now() + timedelta(hours=24)
        )
        
        self.assertEqual(backup.code, 'TESTCODE1')
        self.assertFalse(backup.is_used)
        self.assertIsNone(backup.used_at)
    
    def test_backup_code_expiration_check(self):
        """Test backup code expiration check"""
        # Create non-expired code
        valid_code = BackupCode.objects.create(
            user_profile=self.profile,
            code='VALID001',
            expires_at=now() + timedelta(hours=24)
        )
        self.assertFalse(valid_code.is_expired())
        
        # Create expired code
        expired_code = BackupCode.objects.create(
            user_profile=self.profile,
            code='EXPIRED01',
            expires_at=now() - timedelta(hours=1)
        )
        self.assertTrue(expired_code.is_expired())
    
    def test_backup_code_time_until_expiration(self):
        """Test time until expiration calculation"""
        future_time = now() + timedelta(hours=24)
        backup = BackupCode.objects.create(
            user_profile=self.profile,
            code='FUTURE001',
            expires_at=future_time
        )
        
        time_left = backup.time_until_expiration()
        self.assertIsNotNone(time_left)
        self.assertGreater(time_left.total_seconds(), 0)


class ImportedFileTests(TestCase):
    """Test ImportedFile model"""
    
    def test_imported_file_creation(self):
        """Test creating an imported file record"""
        imported = ImportedFile.objects.create(
            filename='test_inventory.xlsx',
            file_hash='abc123def456',
            file_size=102400,
            records_imported=50,
            status='success'
        )
        
        self.assertEqual(imported.filename, 'test_inventory.xlsx')
        self.assertEqual(imported.records_imported, 50)
        self.assertEqual(imported.status, 'success')
    
    def test_imported_file_with_error(self):
        """Test creating an imported file with error"""
        imported = ImportedFile.objects.create(
            filename='bad_file.xlsx',
            file_hash='xyz789',
            file_size=50000,
            records_imported=0,
            status='error',
            error_message='Invalid file format'
        )
        
        self.assertEqual(imported.status, 'error')
        self.assertIn('Invalid', imported.error_message)


class CurrencyUtilsTests(TestCase):
    """Test PHP currency formatting utilities"""
    
    def test_format_php_with_symbol(self):
        """Test formatting number as PHP with symbol"""
        from .utils import format_php
        
        result = format_php(1234.56)
        self.assertEqual(result, '₱1,234.56')
    
    def test_format_php_without_symbol(self):
        """Test formatting number as PHP without symbol"""
        from .utils import format_php
        
        result = format_php(1234.56, include_symbol=False)
        self.assertEqual(result, '1,234.56')
    
    def test_format_php_large_number(self):
        """Test formatting large PHP amount"""
        from .utils import format_php
        
        result = format_php(1000000.00)
        self.assertEqual(result, '₱1,000,000.00')
    
    def test_format_php_decimal_input(self):
        """Test formatting Decimal as PHP"""
        from .utils import format_php
        
        result = format_php(Decimal('5000.75'))
        self.assertEqual(result, '₱5,000.75')
    
    def test_format_php_zero(self):
        """Test formatting zero as PHP"""
        from .utils import format_php
        
        result = format_php(0)
        self.assertEqual(result, '₱0.00')
    
    def test_format_php_small_amount(self):
        """Test formatting small PHP amount"""
        from .utils import format_php
        
        result = format_php(50.25)
        self.assertEqual(result, '₱50.25')
    
    def test_php_to_decimal(self):
        """Test converting PHP string to Decimal"""
        from .utils import php_to_decimal
        
        result = php_to_decimal('₱1,234.56')
        self.assertEqual(result, Decimal('1234.56'))
    
    def test_php_to_decimal_without_symbol(self):
        """Test converting PHP string without symbol to Decimal"""
        from .utils import php_to_decimal
        
        result = php_to_decimal('1,000.00')
        self.assertEqual(result, Decimal('1000.00'))
    
    def test_get_currency_symbol(self):
        """Test getting PHP currency symbol"""
        from .utils import get_currency_symbol
        
        result = get_currency_symbol()
        self.assertEqual(result, '₱')
    
    def test_get_currency_code(self):
        """Test getting PHP currency code"""
        from .utils import get_currency_code
        
        result = get_currency_code()
        self.assertEqual(result, 'PHP')
    
    def test_get_currency_name(self):
        """Test getting PHP currency name"""
        from .utils import get_currency_name
        
        result = get_currency_name()
        self.assertEqual(result, 'Philippine Peso')


class SettingsConfigTests(TestCase):
    """Test settings configuration for multi-currency and multi-timezone support"""
    
    def test_get_currency_config_php(self):
        """Test getting PHP currency configuration"""
        from .settings_config import get_currency_config
        
        config = get_currency_config('PHP')
        self.assertEqual(config['code'], 'PHP')
        self.assertEqual(config['symbol'], '₱')
        self.assertEqual(config['name'], 'Philippine Peso')
    
    def test_get_currency_config_usd(self):
        """Test getting USD currency configuration"""
        from .settings_config import get_currency_config
        
        config = get_currency_config('USD')
        self.assertEqual(config['code'], 'USD')
        self.assertEqual(config['symbol'], '$')
        self.assertEqual(config['name'], 'US Dollar')
    
    def test_get_currency_config_eur(self):
        """Test getting EUR currency configuration"""
        from .settings_config import get_currency_config
        
        config = get_currency_config('EUR')
        self.assertEqual(config['code'], 'EUR')
        self.assertEqual(config['symbol'], '€')
        self.assertEqual(config['name'], 'Euro')
    
    def test_get_supported_currencies(self):
        """Test getting list of supported currencies"""
        from .settings_config import get_supported_currencies
        
        currencies = get_supported_currencies()
        self.assertIn('PHP', currencies)
        self.assertIn('USD', currencies)
        self.assertIn('EUR', currencies)
    
    def test_get_timezone_config_pht(self):
        """Test getting PHT timezone configuration"""
        from .settings_config import get_timezone_config
        
        config = get_timezone_config('PHT')
        self.assertEqual(config['code'], 'PHT')
        self.assertEqual(config['timezone'], 'Asia/Manila')
        self.assertEqual(config['offset'], '+08:00')
        self.assertEqual(config['name'], 'Philippine Time')
    
    def test_get_timezone_config_est(self):
        """Test getting EST timezone configuration"""
        from .settings_config import get_timezone_config
        
        config = get_timezone_config('EST')
        self.assertEqual(config['code'], 'EST')
        self.assertEqual(config['timezone'], 'US/Eastern')
        self.assertEqual(config['offset'], '-05:00')
    
    def test_get_timezone_config_utc(self):
        """Test getting UTC timezone configuration"""
        from .settings_config import get_timezone_config
        
        config = get_timezone_config('UTC')
        self.assertEqual(config['code'], 'UTC')
        self.assertEqual(config['timezone'], 'UTC')
        self.assertEqual(config['offset'], '+00:00')
    
    def test_get_supported_timezones(self):
        """Test getting list of supported timezones"""
        from .settings_config import get_supported_timezones
        
        timezones = get_supported_timezones()
        self.assertIn('PHT', timezones)
        self.assertIn('EST', timezones)
        self.assertIn('UTC', timezones)
        self.assertIn('CET', timezones)
    
    def test_set_currency(self):
        """Test setting default currency"""
        from .settings_config import set_currency, DEFAULT_CURRENCY
        
        result = set_currency('USD')
        self.assertTrue(result)
    
    def test_set_timezone(self):
        """Test setting default timezone"""
        from .settings_config import set_timezone
        
        result = set_timezone('EST')
        self.assertTrue(result)
    
    def test_set_invalid_currency(self):
        """Test setting invalid currency"""
        from .settings_config import set_currency
        
        result = set_currency('INVALID')
        self.assertFalse(result)
    
    def test_set_invalid_timezone(self):
        """Test setting invalid timezone"""
        from .settings_config import set_timezone
        
        result = set_timezone('INVALID')
        self.assertFalse(result)


class MultiCurrencyUtilsTests(TestCase):
    """Test multi-currency support in utils"""
    
    def test_format_currency_usd(self):
        """Test formatting as USD"""
        from .utils import format_currency
        
        result = format_currency(1234.56, 'USD')
        self.assertEqual(result, '$1,234.56')
    
    def test_format_currency_eur(self):
        """Test formatting as EUR"""
        from .utils import format_currency
        
        result = format_currency(1234.56, 'EUR')
        self.assertEqual(result, '€1,234.56')
    
    def test_format_currency_without_symbol(self):
        """Test formatting currency without symbol"""
        from .utils import format_currency
        
        result = format_currency(1234.56, 'USD', include_symbol=False)
        self.assertEqual(result, '1,234.56')
    
    def test_currency_to_decimal_usd(self):
        """Test converting USD string to Decimal"""
        from .utils import currency_to_decimal
        
        result = currency_to_decimal('$1,234.56', 'USD')
        self.assertEqual(result, Decimal('1234.56'))
    
    def test_currency_to_decimal_eur(self):
        """Test converting EUR string to Decimal"""
        from .utils import currency_to_decimal
        
        result = currency_to_decimal('€1,234.56', 'EUR')
        self.assertEqual(result, Decimal('1234.56'))
    
    def test_get_currency_symbol_usd(self):
        """Test getting USD currency symbol"""
        from .utils import get_currency_symbol
        
        result = get_currency_symbol('USD')
        self.assertEqual(result, '$')
    
    def test_get_currency_symbol_eur(self):
        """Test getting EUR currency symbol"""
        from .utils import get_currency_symbol
        
        result = get_currency_symbol('EUR')
        self.assertEqual(result, '€')
    
    def test_get_currency_code_usd(self):
        """Test getting USD currency code"""
        from .utils import get_currency_code
        
        result = get_currency_code('USD')
        self.assertEqual(result, 'USD')
    
    def test_get_currency_name_usd(self):
        """Test getting USD currency name"""
        from .utils import get_currency_name
        
        result = get_currency_name('USD')
        self.assertEqual(result, 'US Dollar')
