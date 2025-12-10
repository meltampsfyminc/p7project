# Multi-Currency and Multi-Timezone Scalability Guide

## Overview

The property management system now supports **multi-currency** and **multi-timezone** configurations, making it scalable for operations across different regions and currencies. This guide explains how to use, configure, and extend the system for additional currencies and timezones.

---

## Supported Currencies

### Current Implementation

The system currently supports three currencies:

| Currency | Code | Symbol | Name |
|----------|------|--------|------|
| Philippine Peso | `PHP` | ₱ | Philippine Peso |
| US Dollar | `USD` | $ | US Dollar |
| Euro | `EUR` | € | Euro |

### Currency Configuration Location

**File:** `properties/settings_config.py`

```python
CURRENCIES = {
    'PHP': {
        'code': 'PHP',
        'symbol': '₱',
        'name': 'Philippine Peso',
        'decimal_places': 2,
        'thousand_separator': ',',
    },
    'USD': {
        'code': 'USD',
        'symbol': '$',
        'name': 'US Dollar',
        'decimal_places': 2,
        'thousand_separator': ',',
    },
    'EUR': {
        'code': 'EUR',
        'symbol': '€',
        'name': 'Euro',
        'decimal_places': 2,
        'thousand_separator': ',',
    },
}
```

---

## Supported Timezones

### Current Implementation

The system currently supports four timezones:

| Timezone | Code | Python Timezone | Offset | Name |
|----------|------|-----------------|--------|------|
| Philippine Time | `PHT` | `Asia/Manila` | +08:00 | Philippine Time |
| Eastern Standard Time | `EST` | `US/Eastern` | -05:00 | Eastern Standard Time |
| UTC | `UTC` | `UTC` | +00:00 | Coordinated Universal Time |
| Central European Time | `CET` | `Europe/Paris` | +01:00 | Central European Time |

### Timezone Configuration Location

**File:** `properties/settings_config.py`

```python
TIMEZONES = {
    'PHT': {
        'code': 'PHT',
        'timezone': 'Asia/Manila',
        'offset': '+08:00',
        'name': 'Philippine Time',
    },
    'EST': {
        'code': 'EST',
        'timezone': 'US/Eastern',
        'offset': '-05:00',
        'name': 'Eastern Standard Time',
    },
    'UTC': {
        'code': 'UTC',
        'timezone': 'UTC',
        'offset': '+00:00',
        'name': 'Coordinated Universal Time',
    },
    'CET': {
        'code': 'CET',
        'timezone': 'Europe/Paris',
        'offset': '+01:00',
        'name': 'Central European Time',
    },
}
```

---

## Using Multi-Currency Support

### Currency Formatting

**Function:** `format_currency(amount, currency_code, include_symbol=True)`

Format numbers in any supported currency:

```python
from properties.utils import format_currency

# Format as PHP (Philippine Peso)
format_currency(1234.56, 'PHP')  # Returns: '₱1,234.56'

# Format as USD (US Dollar)
format_currency(1234.56, 'USD')  # Returns: '$1,234.56'

# Format as EUR (Euro)
format_currency(1234.56, 'EUR')  # Returns: '€1,234.56'

# Format without symbol
format_currency(1234.56, 'USD', include_symbol=False)  # Returns: '1,234.56'
```

### Currency Conversion

**Function:** `currency_to_decimal(value, currency_code)`

Convert formatted currency strings back to Decimal values:

```python
from properties.utils import currency_to_decimal

# Parse PHP formatted string
currency_to_decimal('₱1,234.56', 'PHP')  # Returns: Decimal('1234.56')

# Parse USD formatted string
currency_to_decimal('$1,234.56', 'USD')  # Returns: Decimal('1234.56')

# Parse EUR formatted string
currency_to_decimal('€1,234.56', 'EUR')  # Returns: Decimal('1234.56')
```

### Getting Currency Information

**Functions:** `get_currency_symbol()`, `get_currency_code()`, `get_currency_name()`

```python
from properties.utils import get_currency_symbol, get_currency_code, get_currency_name

# Get currency symbol
get_currency_symbol('USD')  # Returns: '$'
get_currency_symbol('EUR')  # Returns: '€'
get_currency_symbol('PHP')  # Returns: '₱'

# Get currency code
get_currency_code('USD')  # Returns: 'USD'

# Get currency name
get_currency_name('EUR')  # Returns: 'Euro'
```

### Backwards Compatibility

The old `format_php()` function still works for backward compatibility:

```python
from properties.utils import format_php, php_to_decimal

format_php(1234.56)  # Returns: '₱1,234.56'
php_to_decimal('₱1,234.56')  # Returns: Decimal('1234.56')
```

---

## Using Multi-Timezone Support

### Timezone Conversion

**Function:** `convert_to_timezone(datetime, timezone_code)`

Convert a datetime to any supported timezone:

```python
from properties.timezone_utils import convert_to_timezone
from django.utils import timezone

now = timezone.now()

# Convert to Philippine Time
pht_time = convert_to_timezone(now, 'PHT')

# Convert to Eastern Standard Time
est_time = convert_to_timezone(now, 'EST')

# Convert to UTC
utc_time = convert_to_timezone(now, 'UTC')

# Convert to Central European Time
cet_time = convert_to_timezone(now, 'CET')
```

### Getting Current Time in Timezone

**Function:** `get_now_in_timezone(timezone_code)`

Get the current time in a specific timezone:

```python
from properties.timezone_utils import get_now_in_timezone

# Get current time in Philippine Time
now_pht = get_now_in_timezone('PHT')

# Get current time in Eastern Standard Time
now_est = get_now_in_timezone('EST')
```

### Formatting Datetime for Display

**Function:** `format_datetime_in_timezone(datetime, timezone_code, format_str)`

Format datetime in a specific timezone for display:

```python
from properties.timezone_utils import format_datetime_in_timezone
from django.utils import timezone

now = timezone.now()

# Format in Philippine Time (default format)
formatted = format_datetime_in_timezone(now, 'PHT')
# Returns: '2024-01-15 14:30:45 PST'

# Format with custom format string
formatted = format_datetime_in_timezone(now, 'EST', '%Y-%m-%d %I:%M %p')
# Returns: '2024-01-15 02:30 PM'
```

### Getting Timezone Information

**Functions:** `get_timezone_offset()`, `get_timezone_name()`, `get_supported_timezones()`

```python
from properties.timezone_utils import get_timezone_offset, get_timezone_name, get_supported_timezones

# Get timezone offset
get_timezone_offset('PHT')  # Returns: '+08:00'
get_timezone_offset('EST')  # Returns: '-05:00'

# Get timezone name
get_timezone_name('CET')  # Returns: 'Central European Time'

# Get all supported timezones
timezones = get_supported_timezones()
# Returns: dict with all timezone configurations
```

---

## User Preferences Model Integration

Each user can now set their preferred currency and timezone in their profile:

```python
from django.contrib.auth.models import User
from properties.models import UserProfile

# Get user profile
user = User.objects.get(username='johndoe')
profile = user.profile

# Set user's preferred timezone
profile.timezone = 'EST'

# Set user's preferred currency
profile.currency = 'USD'

profile.save()

# Access user preferences
print(f"User's timezone: {profile.timezone}")
print(f"User's currency: {profile.currency}")
```

### Available User Preferences

The `UserProfile` model includes:

```python
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
```

---

## Extending the System

### Adding a New Currency

To add a new currency (e.g., JPY - Japanese Yen):

1. **Update `properties/settings_config.py`:**

```python
CURRENCIES = {
    # ... existing currencies ...
    'JPY': {
        'code': 'JPY',
        'symbol': '¥',
        'name': 'Japanese Yen',
        'decimal_places': 0,  # JPY doesn't use decimal places
        'thousand_separator': ',',
    },
}
```

2. **Update UserProfile choices in `properties/models.py`:**

```python
CURRENCY_CHOICES = [
    # ... existing choices ...
    ('JPY', 'Japanese Yen (¥)'),
]
```

3. **Create a migration:**

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Add tests in `properties/tests.py`:**

```python
def test_format_currency_jpy(self):
    from .utils import format_currency
    result = format_currency(100000, 'JPY')
    self.assertEqual(result, '¥100,000')
```

### Adding a New Timezone

To add a new timezone (e.g., JST - Japan Standard Time):

1. **Update `properties/settings_config.py`:**

```python
TIMEZONES = {
    # ... existing timezones ...
    'JST': {
        'code': 'JST',
        'timezone': 'Asia/Tokyo',
        'offset': '+09:00',
        'name': 'Japan Standard Time',
    },
}
```

2. **Update UserProfile choices in `properties/models.py`:**

```python
TIMEZONE_CHOICES = [
    # ... existing choices ...
    ('JST', 'Japan Standard Time (UTC+09:00)'),
]
```

3. **Create a migration:**

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Add tests in `properties/tests.py`:**

```python
def test_get_timezone_config_jst(self):
    from .settings_config import get_timezone_config
    config = get_timezone_config('JST')
    self.assertEqual(config['timezone'], 'Asia/Tokyo')
```

---

## Configuration Management

### Setting System Default Currency

**Function:** `set_currency(currency_code)`

```python
from properties.settings_config import set_currency

# Set default currency for the system
set_currency('USD')  # Returns: True

# Invalid currency code
set_currency('INVALID')  # Returns: False
```

### Setting System Default Timezone

**Function:** `set_timezone(timezone_code)`

```python
from properties.settings_config import set_timezone

# Set default timezone for the system
set_timezone('EST')  # Returns: True

# Invalid timezone code
set_timezone('INVALID')  # Returns: False
```

### Getting Current Defaults

```python
from properties.settings_config import get_active_currency, get_active_timezone

# Get current default currency configuration
current_currency = get_active_currency()
# Returns: {'code': 'PHP', 'symbol': '₱', 'name': 'Philippine Peso', ...}

# Get current default timezone configuration
current_timezone = get_active_timezone()
# Returns: {'code': 'PHT', 'timezone': 'Asia/Manila', ...}
```

---

## Best Practices

### 1. Always Specify Currency Code

When using currency utilities, always specify the currency code explicitly:

```python
# Good - Explicit currency
format_currency(amount, 'USD')

# Avoid - Relies on default
format_currency(amount)  # Uses system default
```

### 2. Store Amounts as Decimal

Always store monetary amounts as Decimal in the database:

```python
from decimal import Decimal

# Good
amount = Decimal('1234.56')

# Avoid
amount = 1234.56  # Float can cause rounding errors
```

### 3. Use User Preferences

When displaying data to users, respect their currency and timezone preferences:

```python
user_profile = request.user.profile
formatted_amount = format_currency(amount, user_profile.currency)
user_datetime = convert_to_timezone(datetime, user_profile.timezone)
```

### 4. Handle Timezone-Aware Datetimes

Always work with timezone-aware datetime objects:

```python
from django.utils import timezone

# Good - Timezone-aware
dt = timezone.now()

# Avoid - Naive datetime
dt = datetime.datetime.now()
```

---

## Testing

### Running Tests

All multi-currency and multi-timezone tests are included:

```bash
# Run all tests
python manage.py test properties

# Run only configuration tests
python manage.py test properties.tests.SettingsConfigTests

# Run only multi-currency tests
python manage.py test properties.tests.MultiCurrencyUtilsTests

# Run specific test
python manage.py test properties.tests.SettingsConfigTests.test_get_currency_config_php
```

### Test Coverage

- **12 SettingsConfigTests:** Currency and timezone configuration
- **9 MultiCurrencyUtilsTests:** Multi-currency formatting and parsing
- **Total: 68 tests** covering all system functionality

---

## Examples

### Example 1: Format Financial Data in User's Currency

```python
from properties.utils import format_currency

def display_property_value(user, property_obj):
    """Display property value in user's preferred currency"""
    user_currency = user.profile.currency
    formatted_value = format_currency(
        property_obj.price,
        user_currency
    )
    return f"Property Value: {formatted_value}"
```

### Example 2: Display Dates in User's Timezone

```python
from properties.timezone_utils import format_datetime_in_timezone

def display_transaction_date(user, transaction):
    """Display transaction date in user's timezone"""
    user_timezone = user.profile.timezone
    formatted_date = format_datetime_in_timezone(
        transaction.created_at,
        user_timezone,
        '%Y-%m-%d %H:%M:%S'
    )
    return f"Date: {formatted_date}"
```

### Example 3: Multi-Region Report

```python
from properties.utils import format_currency
from properties.timezone_utils import format_datetime_in_timezone

def generate_region_report(regions):
    """Generate report for multiple regions with their currencies"""
    report = []
    
    for region in regions:
        users = region.users.all()
        for user in users:
            data = {
                'region': region.name,
                'currency': user.profile.currency,
                'timezone': user.profile.timezone,
                'total_assets': format_currency(
                    user.total_assets,
                    user.profile.currency
                ),
                'last_updated': format_datetime_in_timezone(
                    user.last_updated,
                    user.profile.timezone
                ),
            }
            report.append(data)
    
    return report
```

---

## Troubleshooting

### Issue: Currency Symbol Not Displaying

**Cause:** Database encoding issue with special characters

**Solution:** Ensure database is UTF-8 encoded

```sql
ALTER DATABASE property_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue: Timezone Offset Incorrect

**Cause:** Using pytz directly without proper configuration

**Solution:** Always use `convert_to_timezone()` function which handles DST automatically

```python
# Wrong - Might not handle DST
tz = pytz.timezone('US/Eastern')

# Correct - Handles DST automatically
from properties.timezone_utils import convert_to_timezone
dt = convert_to_timezone(datetime, 'EST')
```

### Issue: Decimal Conversion Error

**Cause:** Attempting to parse currency string with incorrect symbol

**Solution:** Ensure currency code matches the string format

```python
# Wrong - Symbol mismatch
currency_to_decimal('₱1,234.56', 'USD')  # Will fail

# Correct - Symbol matches
currency_to_decimal('₱1,234.56', 'PHP')
```

---

## Summary

The property management system is now fully scalable for:

- ✅ **Multiple Currencies:** PHP, USD, EUR (easily extensible)
- ✅ **Multiple Timezones:** PHT, EST, UTC, CET (easily extensible)
- ✅ **User Preferences:** Each user can set preferred currency and timezone
- ✅ **Easy Configuration:** Simple configuration-based approach in `settings_config.py`
- ✅ **Comprehensive Testing:** 68 tests covering all functionality
- ✅ **Backward Compatible:** Old `format_php()` functions still work

Future expansion to other currencies and timezones requires minimal code changes and can be done by simply updating `properties/settings_config.py` and creating migrations.
