import pandas as pd
from typing import Set
from ...domain.value_objects.date_range import DateRange
from ..logging.logger_service import get_logger_service
from ..logging.decorators import log_operation


class TradingDayService:
    """Service for determining trading days based on actual market data patterns."""
    
    def __init__(self):
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("infrastructure")
    
    @log_operation("trading_days", include_args=True, include_result=True)
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
        
        self._logger.debug(f"Identified {len(trading_days)} potential trading days in range {date_range.start} to {date_range.end}")
        
        return trading_days
    
    @log_operation("trading_days", include_args=True, include_result=True)
    def filter_actual_trading_days(self, ticker: str, potential_trading_days: Set[str], 
                                 actual_data_dates: Set[str]) -> Set[str]:
        """
        Filter potential trading days to only include those where we actually have data.
        
        This ensures we only consider days that Yahoo Finance actually returns data for,
        which respects the current product's understanding of trading days.
        """
        # Only include days that are both potential trading days AND have actual data
        actual_trading_days = potential_trading_days.intersection(actual_data_dates)
        
        self._logger.debug(f"Filtered to {len(actual_trading_days)} actual trading days for {ticker}")
        
        return actual_trading_days
    
    @log_operation("trading_days", include_args=True, include_result=True)
    def get_trading_days_from_data(self, price_data: pd.Series) -> Set[str]:
        """Extract trading days from actual price data."""
        if price_data.empty:
            return set()
        
        # Convert index to string dates
        trading_days = {date.strftime('%Y-%m-%d') for date in price_data.index}
        
        self._logger.debug(f"Extracted {len(trading_days)} trading days from price data")
        
        return trading_days
