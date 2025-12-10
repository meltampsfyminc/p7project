"""
Timezone utilities for handling multiple timezones
Supports PHT, EST, UTC, CET and can be extended for additional timezones
"""
from datetime import datetime
import pytz
from django.utils import timezone as django_timezone
from .settings_config import get_active_timezone, get_timezone_config


def convert_to_timezone(dt: datetime, timezone_code: str = None) -> datetime:
    """
    Convert a datetime to a specific timezone
    
    Args:
        dt: Datetime object (should be timezone-aware)
        timezone_code: Timezone code (e.g., 'PHT', 'EST', 'UTC')
                      If None, uses system default timezone
    
    Returns:
        Datetime object in the specified timezone
    
    Examples:
        >>> convert_to_timezone(django_timezone.now(), 'PHT')
        # Returns current time in Philippine Time
    """
    config = get_timezone_config(timezone_code)
    tz = pytz.timezone(config['timezone'])
    
    # Make sure datetime is timezone-aware
    if dt.tzinfo is None:
        dt = django_timezone.make_aware(dt)
    
    return dt.astimezone(tz)


def convert_to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC
    
    Args:
        dt: Datetime object (should be timezone-aware)
    
    Returns:
        Datetime object in UTC
    """
    return convert_to_timezone(dt, 'UTC')


def get_now_in_timezone(timezone_code: str = None) -> datetime:
    """
    Get current time in a specific timezone
    
    Args:
        timezone_code: Timezone code (e.g., 'PHT', 'EST', 'UTC')
                      If None, uses system default timezone
    
    Returns:
        Current datetime in the specified timezone
    """
    return convert_to_timezone(django_timezone.now(), timezone_code)


def format_datetime_in_timezone(dt: datetime, timezone_code: str = None, format_str: str = None) -> str:
    """
    Format a datetime for display in a specific timezone
    
    Args:
        dt: Datetime object
        timezone_code: Timezone code (e.g., 'PHT', 'EST', 'UTC')
                      If None, uses system default timezone
        format_str: Python datetime format string
                   If None, uses default: '%Y-%m-%d %H:%M:%S %Z'
    
    Returns:
        Formatted datetime string
    
    Examples:
        >>> format_datetime_in_timezone(django_timezone.now(), 'PHT')
        '2024-01-15 14:30:45 PST'
    """
    if format_str is None:
        format_str = '%Y-%m-%d %H:%M:%S %Z'
    
    converted_dt = convert_to_timezone(dt, timezone_code)
    return converted_dt.strftime(format_str)


def get_timezone_offset(timezone_code: str = None) -> str:
    """
    Get timezone offset from UTC
    
    Args:
        timezone_code: Timezone code (e.g., 'PHT', 'EST', 'UTC')
                      If None, uses system default timezone
    
    Returns:
        Offset string (e.g., '+08:00', '-05:00', '+00:00')
    """
    config = get_timezone_config(timezone_code)
    return config['offset']


def get_timezone_name(timezone_code: str = None) -> str:
    """
    Get timezone name
    
    Args:
        timezone_code: Timezone code (e.g., 'PHT', 'EST', 'UTC')
                      If None, uses system default timezone
    
    Returns:
        Timezone name string
    """
    config = get_timezone_config(timezone_code)
    return config['name']


def get_supported_timezones() -> dict:
    """
    Get list of all supported timezones with their configurations
    
    Returns:
        Dictionary of supported timezones
    """
    from .settings_config import TIMEZONES
    return TIMEZONES
