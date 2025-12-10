"""
System Settings and Configuration
Supports multiple currencies and timezones for future scalability
"""

# Supported currencies
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

# Supported timezones
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

# Current system configuration (can be changed based on environment variables or settings)
DEFAULT_CURRENCY = 'PHP'  # Default to Philippine Peso
DEFAULT_TIMEZONE = 'PHT'  # Default to Philippine Time

# Configuration override method for environment-specific settings
def get_currency_config(currency_code=None):
    """
    Get currency configuration
    
    Args:
        currency_code: Currency code (e.g., 'PHP', 'USD', 'EUR')
                      If None, uses DEFAULT_CURRENCY
    
    Returns:
        Dictionary with currency configuration
    """
    code = currency_code or DEFAULT_CURRENCY
    return CURRENCIES.get(code, CURRENCIES[DEFAULT_CURRENCY])


def get_timezone_config(timezone_code=None):
    """
    Get timezone configuration
    
    Args:
        timezone_code: Timezone code (e.g., 'PHT', 'EST', 'UTC')
                      If None, uses DEFAULT_TIMEZONE
    
    Returns:
        Dictionary with timezone configuration
    """
    code = timezone_code or DEFAULT_TIMEZONE
    return TIMEZONES.get(code, TIMEZONES[DEFAULT_TIMEZONE])


def get_active_currency():
    """Get the currently active currency configuration"""
    return get_currency_config(DEFAULT_CURRENCY)


def get_active_timezone():
    """Get the currently active timezone configuration"""
    return get_timezone_config(DEFAULT_TIMEZONE)


def set_currency(currency_code):
    """
    Set the default currency for the system
    
    Note: In production, this should be set via environment variables
    or Django settings, not changed at runtime.
    
    Args:
        currency_code: Currency code to set as default
    
    Returns:
        True if successful, False if invalid currency code
    """
    global DEFAULT_CURRENCY
    if currency_code in CURRENCIES:
        DEFAULT_CURRENCY = currency_code
        return True
    return False


def set_timezone(timezone_code):
    """
    Set the default timezone for the system
    
    Note: In production, this should be set via environment variables
    or Django settings, not changed at runtime.
    
    Args:
        timezone_code: Timezone code to set as default
    
    Returns:
        True if successful, False if invalid timezone code
    """
    global DEFAULT_TIMEZONE
    if timezone_code in TIMEZONES:
        DEFAULT_TIMEZONE = timezone_code
        return True
    return False


def get_supported_currencies():
    """Get list of supported currency codes"""
    return list(CURRENCIES.keys())


def get_supported_timezones():
    """Get list of supported timezone codes"""
    return list(TIMEZONES.keys())
