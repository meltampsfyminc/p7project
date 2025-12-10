"""
Currency and timezone utilities for formatting and handling multiple currencies
Supports PHP, USD, EUR and can be extended for additional currencies/timezones
"""
from decimal import Decimal
from typing import Union
from .settings_config import get_active_currency, get_currency_config


def format_currency(amount: Union[int, float, Decimal], currency_code: str = None, include_symbol: bool = True) -> str:
    """
    Format a number as specified currency
    
    Args:
        amount: The amount to format (int, float, or Decimal)
        currency_code: Currency code (e.g., 'PHP', 'USD', 'EUR')
                      If None, uses system default currency
        include_symbol: Whether to include the currency symbol (default: True)
    
    Returns:
        Formatted string (e.g., '₱1,234.56', '$1,234.56', '€1,234.56')
    
    Examples:
        >>> format_currency(1234.56, 'PHP')
        '₱1,234.56'
        >>> format_currency(1234.56, 'USD')
        '$1,234.56'
        >>> format_currency(1234.56, 'EUR')
        '€1,234.56'
    """
    # Get currency configuration
    config = get_currency_config(currency_code)
    
    # Convert to Decimal for precise handling
    try:
        amount_decimal = Decimal(str(amount))
    except (ValueError, TypeError):
        return config['symbol'] + '0.00' if include_symbol else '0.00'
    
    # Format with specified decimal places and thousand separators
    decimal_places = config['decimal_places']
    format_string = "{{:,.{:d}f}}".format(decimal_places)
    formatted = format_string.format(amount_decimal)
    
    if include_symbol:
        return f"{config['symbol']}{formatted}"
    return formatted


def format_php(amount: Union[int, float, Decimal], include_symbol: bool = True) -> str:
    """
    Format a number as Philippine Peso (PHP) - backwards compatibility wrapper
    
    Args:
        amount: The amount to format (int, float, or Decimal)
        include_symbol: Whether to include the ₱ symbol (default: True)
    
    Returns:
        Formatted string (e.g., '₱1,234.56' or '1,234.56')
    
    Examples:
        >>> format_php(1234.56)
        '₱1,234.56'
        >>> format_php(1234.56, include_symbol=False)
        '1,234.56'
    """
    return format_currency(amount, 'PHP', include_symbol)


def currency_to_decimal(value: str, currency_code: str = None) -> Decimal:
    """
    Convert a currency formatted string to Decimal
    
    Args:
        value: Formatted currency string (e.g., '₱1,234.56', '$1,234.56', '€1,234.56')
        currency_code: Currency code to determine which symbol to remove
                      If None, tries to remove any common currency symbol
    
    Returns:
        Decimal value
    
    Examples:
        >>> currency_to_decimal('₱1,234.56', 'PHP')
        Decimal('1234.56')
        >>> currency_to_decimal('$1,234.56', 'USD')
        Decimal('1234.56')
    """
    # Get currency configuration
    config = get_currency_config(currency_code)
    
    # Remove currency symbol and thousand separators
    cleaned = value.replace(config['symbol'], '').replace(',', '').strip()
    try:
        return Decimal(cleaned)
    except (ValueError, TypeError):
        return Decimal('0.00')


def php_to_decimal(value: str) -> Decimal:
    """
    Convert a PHP formatted string to Decimal (backwards compatibility)
    
    Args:
        value: Formatted PHP string (e.g., '₱1,234.56' or '1,234.56')
    
    Returns:
        Decimal value
    
    Examples:
        >>> php_to_decimal('₱1,234.56')
        Decimal('1234.56')
        >>> php_to_decimal('1,234.56')
        Decimal('1234.56')
    """
    return currency_to_decimal(value, 'PHP')


def get_currency_symbol(currency_code: str = None) -> str:
    """
    Get currency symbol
    
    Args:
        currency_code: Currency code (e.g., 'PHP', 'USD', 'EUR')
                      If None, uses system default currency
    
    Returns:
        Currency symbol string
    """
    config = get_currency_config(currency_code)
    return config['symbol']


def get_currency_code(currency_code: str = None) -> str:
    """
    Get currency code
    
    Args:
        currency_code: Currency code (e.g., 'PHP', 'USD', 'EUR')
                      If None, uses system default currency
    
    Returns:
        Currency code string
    """
    config = get_currency_config(currency_code)
    return config['code']


def get_currency_name(currency_code: str = None) -> str:
    """
    Get currency name
    
    Args:
        currency_code: Currency code (e.g., 'PHP', 'USD', 'EUR')
                      If None, uses system default currency
    
    Returns:
        Currency name string
    """
    config = get_currency_config(currency_code)
    return config['name']
