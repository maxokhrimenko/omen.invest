"""
Utility functions for date calculations
All calendar calculations use New York timezone for financial data consistency
"""
from datetime import date, datetime, timedelta
from typing import Union
import pytz


def get_ny_date() -> date:
    """
    Gets the current date in New York timezone.
    
    Returns:
        Current date in NY timezone
    """
    ny_tz = pytz.timezone('America/New_York')
    ny_now = datetime.now(ny_tz)
    return ny_now.date()


def get_previous_working_day(reference_date: Union[date, datetime, None] = None) -> date:
    """
    Gets the previous working day (Monday-Friday) from a given date.
    
    Args:
        reference_date: The reference date (defaults to current NY date)
        
    Returns:
        The previous working day as a date object
    """
    if reference_date is None:
        reference_date = get_ny_date()
    
    # Convert datetime to date if needed
    if isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    
    result = reference_date - timedelta(days=1)
    
    # If it's Saturday (5) or Sunday (6), go back to Friday
    if result.weekday() == 5:  # Saturday
        result = result - timedelta(days=1)  # Go back to Friday
    elif result.weekday() == 6:  # Sunday
        result = result - timedelta(days=2)  # Go back to Friday
    
    return result


def is_date_after_previous_working_day(check_date: Union[date, datetime, str], reference_date: Union[date, datetime, None] = None) -> bool:
    """
    Checks if a given date is after the previous working day.
    
    Args:
        check_date: The date to check (can be date, datetime, or string in YYYY-MM-DD format)
        reference_date: The reference date to calculate previous working day from (defaults to current NY date)
        
    Returns:
        True if the date is after the previous working day
    """
    if isinstance(check_date, str):
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    elif isinstance(check_date, datetime):
        check_date = check_date.date()
    
    previous_working_day = get_previous_working_day(reference_date)
    # Compare dates directly (both are date objects, so this works correctly)
    return check_date > previous_working_day


def get_previous_working_day_string(reference_date: Union[date, datetime, None] = None) -> str:
    """
    Gets the previous working day as a string in YYYY-MM-DD format.
    
    Args:
        reference_date: The reference date (defaults to current NY date)
        
    Returns:
        The previous working day as a string
    """
    previous_working_day = get_previous_working_day(reference_date)
    return previous_working_day.strftime('%Y-%m-%d')
