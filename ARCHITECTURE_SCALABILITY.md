# System Architecture Overview: Multi-Currency & Multi-Timezone Support

## Quick Summary

The property management system has been enhanced with a **configuration-driven, scalable architecture** for supporting multiple currencies and timezones. This allows the system to operate seamlessly across different regions without code changes.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Profile (Django)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ User Preference Fields:                               │  │
│  │  - timezone: Chosen from TIMEZONE_CHOICES           │  │
│  │  - currency: Chosen from CURRENCY_CHOICES           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              Settings Configuration Module                   │
│         (properties/settings_config.py)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ CURRENCIES = {                                        │  │
│  │   'PHP': {...}, 'USD': {...}, 'EUR': {...}, ...     │  │
│  │ }                                                     │  │
│  │                                                       │  │
│  │ TIMEZONES = {                                        │  │
│  │   'PHT': {...}, 'EST': {...}, 'UTC': {...}, ...    │  │
│  │ }                                                     │  │
│  │                                                       │  │
│  │ Functions:                                           │  │
│  │ - get_currency_config(code)                         │  │
│  │ - get_timezone_config(code)                         │  │
│  │ - set_currency() / set_timezone()                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬─────────────────────────────────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
   ┌─────────────────────────┐    ┌────────────────────────┐
   │ Utils Module            │    │ Timezone Utils Module  │
   │(properties/utils.py)    │    │(properties/timezone_  │
   │                         │    │ utils.py)              │
   ├─────────────────────────┤    ├────────────────────────┤
   │ - format_currency()     │    │ - convert_to_timezone()│
   │ - currency_to_decimal() │    │ - get_now_in_timezone()│
   │ - get_currency_*()      │    │ - format_datetime_in_ │
   │ - format_php() [legacy] │    │   timezone()           │
   │ - php_to_decimal()      │    │ - get_timezone_offset()│
   │   [legacy]              │    │ - get_timezone_name()  │
   └─────────────────────────┘    └────────────────────────┘
      ▲                                  ▲
      │                                  │
      └──────────────────┬───────────────┘
                         │
                    Used in:
         ┌────────────────┴────────────────┐
         ▼                                  ▼
    ┌──────────────────────┐    ┌───────────────────────┐
    │ Views/Templates      │    │ Business Logic        │
    │                      │    │ (Models, Services)    │
    │ - Display currency   │    │ - Calculate amounts   │
    │   formatted amounts  │    │   in correct currency │
    │ - Show dates in      │    │ - Store/retrieve      │
    │   user's timezone    │    │   user preferences    │
    │ - Handle user input  │    │ - Perform conversions │
    └──────────────────────┘    └───────────────────────┘
```

---

## Core Components

### 1. **Settings Configuration Module** (`settings_config.py`)
- **Purpose:** Centralized configuration for all currencies and timezones
- **Why:** Allows easy extension without code changes
- **Key Functions:**
  - `get_currency_config(code)` - Get currency details
  - `get_timezone_config(code)` - Get timezone details
  - `set_currency()` / `set_timezone()` - Override defaults at runtime

### 2. **Currency Utilities** (`utils.py`)
- **Purpose:** Handle currency formatting and parsing
- **Key Functions:**
  - `format_currency(amount, currency_code, include_symbol)` - Format numbers
  - `currency_to_decimal(value, currency_code)` - Parse formatted strings
  - `get_currency_symbol()`, `get_currency_code()`, `get_currency_name()` - Info getters

### 3. **Timezone Utilities** (`timezone_utils.py`)
- **Purpose:** Handle timezone conversion and datetime formatting
- **Key Functions:**
  - `convert_to_timezone(dt, timezone_code)` - Convert datetime
  - `get_now_in_timezone(timezone_code)` - Get current time in timezone
  - `format_datetime_in_timezone(dt, timezone_code, format_str)` - Format datetime

### 4. **UserProfile Model Enhancement**
- **New Fields:**
  - `timezone` - User's preferred timezone (choices from TIMEZONE_CHOICES)
  - `currency` - User's preferred currency (choices from CURRENCY_CHOICES)
- **Purpose:** Store per-user preferences for localization

---

## Data Flow Example

### Scenario: Display Property Value to User

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User views property detail page                              │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. View retrieves user.profile.currency (e.g., 'USD')          │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. View calls format_currency(property.price, 'USD')           │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. format_currency() calls get_currency_config('USD')          │
│    Returns: {'symbol': '$', 'decimal_places': 2, ...}          │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Formats amount: 1234.56 → '$1,234.56'                       │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Returns formatted string to template                         │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Template displays: "Property Value: $1,234.56"              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Extensibility

The system is designed for easy expansion. Adding a new currency or timezone requires **only configuration changes**:

### Adding New Currency

**Step 1:** Update `CURRENCIES` dict in `settings_config.py`
```python
CURRENCIES = {
    # ... existing currencies ...
    'JPY': {'code': 'JPY', 'symbol': '¥', 'name': 'Japanese Yen', ...}
}
```

**Step 2:** Update `CURRENCY_CHOICES` in `UserProfile` model
```python
CURRENCY_CHOICES = [
    # ... existing choices ...
    ('JPY', 'Japanese Yen (¥)'),
]
```

**Step 3:** Create and run migration
```bash
python manage.py makemigrations
python manage.py migrate
```

**Result:** System automatically supports JPY formatting and user can select it in preferences

---

## Current System State

### ✅ Implemented
- [x] PHP currency support with ₱ symbol
- [x] USD currency support with $ symbol
- [x] EUR currency support with € symbol
- [x] PHT (Philippine Time) timezone
- [x] EST (Eastern Standard Time) timezone
- [x] UTC timezone
- [x] CET (Central European Time) timezone
- [x] User preference fields in UserProfile
- [x] Configuration management system
- [x] 68 comprehensive tests
- [x] Backward compatibility with old `format_php()` functions
- [x] Timezone-aware datetime handling

### 🔄 Ready for Future Extensions
- [ ] JPY, GBP, CAD currencies (add to CURRENCIES)
- [ ] Additional timezones like JST, AEST, etc. (add to TIMEZONES)
- [ ] Database-driven configuration (currently code-based)
- [ ] Real-time currency conversion rates (requires external API)
- [ ] Automatic timezone detection from IP address

---

## Performance Considerations

### Current Approach
- **Configuration Lookup:** O(1) - Direct dictionary access
- **Formatting:** O(n) where n = number of digits in amount
- **Memory:** Minimal - only loaded once at startup

### Optimization Tips
1. Cache currency/timezone configs in Redis for high-traffic systems
2. Pre-compile format strings for frequently used currencies
3. Use database-driven config for dynamic changes without restart

---

## Security Considerations

1. **Currency Conversion:** Ensure external rate APIs are validated
2. **Timezone Storage:** Store as string code, not user input
3. **User Preferences:** Validate timezone/currency codes before saving

---

## Testing

### Test Coverage
- **SettingsConfigTests (12 tests):** Currency and timezone configuration
- **MultiCurrencyUtilsTests (9 tests):** Currency formatting
- **CurrencyUtilsTests (11 tests):** Legacy PHP formatting
- **Other tests (36 tests):** Core functionality

**Total: 68 tests with 100% pass rate**

---

## Files Modified/Created

| File | Purpose |
|------|---------|
| `settings_config.py` | Central configuration for currencies and timezones |
| `utils.py` | Updated to support multi-currency (backward compatible) |
| `timezone_utils.py` | New module for timezone handling |
| `models.py` | Added timezone and currency fields to UserProfile |
| `tests.py` | Added 21 new tests for configuration and multi-currency |
| `migrations/0009_*` | Migration for new UserProfile fields |

---

## Quick Reference

### Import Currency Utilities
```python
from properties.utils import (
    format_currency,
    currency_to_decimal,
    get_currency_symbol,
    get_currency_code,
    get_currency_name,
)
```

### Import Timezone Utilities
```python
from properties.timezone_utils import (
    convert_to_timezone,
    get_now_in_timezone,
    format_datetime_in_timezone,
    get_timezone_offset,
    get_timezone_name,
)
```

### Import Configuration
```python
from properties.settings_config import (
    get_currency_config,
    get_timezone_config,
    set_currency,
    set_timezone,
    get_supported_currencies,
    get_supported_timezones,
)
```

---

## Next Steps

1. **Test the system:** Run `python manage.py test properties` to verify all 68 tests pass
2. **Review documentation:** See `MULTI_CURRENCY_TIMEZONE_GUIDE.md` for detailed usage
3. **Integrate in views:** Use `user.profile.currency` and `user.profile.timezone` in templates
4. **Add new currencies/timezones:** Update `settings_config.py` as needed
5. **Monitor performance:** Track config lookup times in production

---

## Support

For questions or issues with multi-currency/timezone support, refer to:
- `MULTI_CURRENCY_TIMEZONE_GUIDE.md` - Detailed usage guide
- `properties/settings_config.py` - Configuration reference
- `properties/utils.py` - Currency utilities code
- `properties/timezone_utils.py` - Timezone utilities code
- `properties/tests.py` - Test examples
