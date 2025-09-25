import pandas as pd
from typing import Set
from ...domain.value_objects.date_range import DateRange


class TradingDayService:
    """Service for determining trading days based on actual market data patterns."""
    
    def __init__(self):
        pass
    
    def get_trading_days_in_range(self, date_range: DateRange) -> Set[str]:
        """
        Get trading days in the given range.
        
        This uses a heuristic: Monday-Friday are trading days,
        excluding major US holidays. For production use, this should
        be enhanced with actual market calendar data.
        """
        start_date = pd.Timestamp(date_range.start)
        end_date = pd.Timestamp(date_range.end)
        
        # Generate all dates in range
        all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Filter to weekdays (Monday=0, Sunday=6)
        weekdays = all_dates[all_dates.weekday < 5]
        
        # Convert to string format
        trading_days = {date.strftime('%Y-%m-%d') for date in weekdays}
        
        return trading_days
    
    def filter_actual_trading_days(self, ticker: str, potential_trading_days: Set[str], 
                                 actual_data_dates: Set[str]) -> Set[str]:
        """
        Filter potential trading days to only include those where we actually have data.
        
        This ensures we only consider days that Yahoo Finance actually returns data for,
        which respects the current product's understanding of trading days.
        """
        # Only include days that are both potential trading days AND have actual data
        actual_trading_days = potential_trading_days.intersection(actual_data_dates)
        
        return actual_trading_days
    
    def get_trading_days_from_data(self, price_data: pd.Series) -> Set[str]:
        """Extract trading days from actual price data."""
        if price_data.empty:
            return set()
        
        # Convert index to string dates
        trading_days = {date.strftime('%Y-%m-%d') for date in price_data.index}
        
        return trading_days
