import pandas as pd
from typing import List, Dict
from ...application.interfaces.repositories import MarketDataRepository
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money
from ..warehouse.warehouse_service import WarehouseService
from ..warehouse.trading_day_service import TradingDayService
from .yfinance_market_repository import YFinanceMarketRepository


class WarehouseMarketRepository(MarketDataRepository):
    """
    Warehouse-enabled market data repository that implements read-through caching.
    
    This repository wraps the existing YFinanceMarketRepository and adds:
    - Read-through caching using SQLite warehouse
    - Trading-day aware gap filling
    - Idempotent persistence
    - Feature flag support
    """
    
    def __init__(self, warehouse_enabled: bool = True, warehouse_db_path: str = "../database/warehouse/warehouse.sqlite"):
        self.warehouse_enabled = warehouse_enabled
        self.warehouse_service = WarehouseService(warehouse_db_path) if warehouse_enabled else None
        self.trading_day_service = TradingDayService()
        self.yahoo_repo = YFinanceMarketRepository()  # Fallback to original
        
        # Observability counters
        self.warehouse_hits = 0
        self.warehouse_misses = 0
        self.yahoo_calls = 0
        self.missing_range_segments = 0
        self.calendar_skipped_days = 0
    
    def get_price_history(self, tickers: List[Ticker], 
                         date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get historical price data with warehouse caching and batching."""
        if not self.warehouse_enabled:
            return self.yahoo_repo.get_price_history(tickers, date_range)
        
        result = {}
        
        # Process tickers in batches for better performance
        batch_size = min(20, len(tickers))  # Process up to 20 tickers at once
        ticker_batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
        
        for batch_idx, ticker_batch in enumerate(ticker_batches):
            
            # Check warehouse coverage for all tickers in batch
            batch_missing_tickers = []
            batch_warehouse_data = {}
            
            for ticker in ticker_batch:
                try:
                    ticker_result = self._get_ticker_price_history(ticker, date_range)
                    if not ticker_result.empty:
                        batch_warehouse_data[ticker] = ticker_result
                    else:
                        batch_missing_tickers.append(ticker)
                except Exception as e:
                    batch_missing_tickers.append(ticker)
            
            # Fetch missing data from Yahoo in batch
            if batch_missing_tickers:
                try:
                    yahoo_result = self.yahoo_repo.get_price_history(batch_missing_tickers, date_range)
                    for ticker in batch_missing_tickers:
                        if ticker in yahoo_result and not yahoo_result[ticker].empty:
                            batch_warehouse_data[ticker] = yahoo_result[ticker]
                            # Store in warehouse for future use
                            self.warehouse_service.store_price_data(ticker, yahoo_result[ticker])
                except Exception as yahoo_error:
                    pass
            
            # Add batch results to final result
            result.update(batch_warehouse_data)
        
        return result
    
    def _get_ticker_price_history(self, ticker: Ticker, date_range: DateRange) -> pd.Series:
        """Get price history for a single ticker with warehouse caching."""
        
        # Step 1: First, try to get data from warehouse to see what we have
        existing_data = self.warehouse_service.get_price_data(ticker, date_range)
        
        if not existing_data.empty:
            # We have data in warehouse for the requested range
            existing_dates = {date.strftime('%Y-%m-%d') for date in existing_data.index}
            
            # Step 2: Determine trading days in the requested range
            potential_trading_days = self.trading_day_service.get_trading_days_in_range(date_range)
            
            # Step 3: Check if we have sufficient coverage
            coverage_ratio = len(existing_dates.intersection(potential_trading_days)) / len(potential_trading_days)
            
            if coverage_ratio >= 0.8:  # At least 80% coverage
                self.warehouse_hits += 1
                return existing_data  # Return the data directly, no need to fetch more
            else:
                # Calculate missing ranges using potential trading days
                missing_ranges = self.warehouse_service.get_missing_ranges(
                    ticker, date_range, potential_trading_days
                )
        else:
            # No data in warehouse for this range, calculate missing ranges
            potential_trading_days = self.trading_day_service.get_trading_days_in_range(date_range)
            missing_ranges = self.warehouse_service.get_missing_ranges(
                ticker, date_range, potential_trading_days
            )
        
        if missing_ranges:
            self.warehouse_misses += 1
            self.missing_range_segments += len(missing_ranges)
            
            # Step 4: Fetch missing data from Yahoo - batch multiple ranges into single call
            if len(missing_ranges) > 1:
                # If multiple ranges, try to batch them into a single call
                min_date = min(start for start, end in missing_ranges)
                max_date = max(end for start, end in missing_ranges)
                
                # Create date range for the entire missing period
                missing_range = DateRange(min_date, max_date)
                
                # Fetch from Yahoo
                yahoo_data = self.yahoo_repo.get_price_history([ticker], missing_range)
                self.yahoo_calls += 1
                
                if ticker in yahoo_data and not yahoo_data[ticker].empty:
                    # Store in warehouse
                    self.warehouse_service.store_price_data(ticker, yahoo_data[ticker])
            else:
                # Single range - use original logic
                start_date, end_date = missing_ranges[0]
                
                # Create date range for this missing segment
                missing_range = DateRange(start_date, end_date)
                
                # Fetch from Yahoo
                yahoo_data = self.yahoo_repo.get_price_history([ticker], missing_range)
                self.yahoo_calls += 1
                
                if ticker in yahoo_data and not yahoo_data[ticker].empty:
                    # Store in warehouse
                    self.warehouse_service.store_price_data(ticker, yahoo_data[ticker])
        
        # Step 5: Read complete requested range from warehouse
        final_data = self.warehouse_service.get_price_data(ticker, date_range)
        
        return final_data
    
    def get_current_prices(self, tickers: List[Ticker]) -> Dict[Ticker, Money]:
        """Get current prices - always use Yahoo for real-time data."""
        return self.yahoo_repo.get_current_prices(tickers)
    
    def get_benchmark_data(self, benchmark_symbol: str, 
                          date_range: DateRange) -> pd.Series:
        """Get benchmark data (e.g., S&P 500) for Beta calculation with warehouse caching."""
        if not self.warehouse_enabled:
            return self.yahoo_repo.get_benchmark_data(benchmark_symbol, date_range)
        
        # Check if we have benchmark coverage information in warehouse
        if self.warehouse_service.has_benchmark_coverage(benchmark_symbol, date_range):
            # We have coverage information, get the actual data
            existing_benchmark = self.warehouse_service.get_benchmark_data(benchmark_symbol, date_range)
            self.warehouse_hits += 1
            return existing_benchmark
        
        # No coverage information in warehouse, fetch from Yahoo and store
        benchmark_data = self.yahoo_repo.get_benchmark_data(benchmark_symbol, date_range)
        
        # Store in warehouse for future use (including coverage information)
        self.warehouse_service.store_benchmark_data(benchmark_symbol, benchmark_data, date_range)
        
        self.warehouse_misses += 1
        return benchmark_data
    
    def get_dividend_history(self, ticker: Ticker, 
                           date_range: DateRange) -> pd.Series:
        """Get dividend history with warehouse caching."""
        if not self.warehouse_enabled:
            return self.yahoo_repo.get_dividend_history(ticker, date_range)
        
        # Check if we have dividend coverage information in warehouse
        if self.warehouse_service.has_dividend_coverage(ticker, date_range):
            # We have coverage information, get the actual data
            existing_dividends = self.warehouse_service.get_dividend_data(ticker, date_range)
            self.warehouse_hits += 1
            return existing_dividends
        
        # No coverage information in warehouse, fetch from Yahoo and store
        dividend_data = self.yahoo_repo.get_dividend_history(ticker, date_range)
        
        # Store in warehouse for future use (including coverage information)
        self.warehouse_service.store_dividend_data(ticker, dividend_data, date_range)
        
        self.warehouse_misses += 1
        return dividend_data
    
    def get_observability_metrics(self) -> Dict[str, int]:
        """Get observability metrics for monitoring."""
        return {
            "warehouse_hits": self.warehouse_hits,
            "warehouse_misses": self.warehouse_misses,
            "yahoo_calls": self.yahoo_calls,
            "missing_range_segments": self.missing_range_segments,
            "calendar_skipped_days": self.calendar_skipped_days,
            "database_size_bytes": self.warehouse_service.get_database_size() if self.warehouse_enabled else 0
        }
    
    def get_price_history_batch(self, tickers: List[Ticker], date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get price history for multiple tickers with warehouse caching."""
        if not self.warehouse_enabled:
            return self.yahoo_repo.get_price_history(tickers, date_range)
        
        # Use warehouse service's optimized batch method
        return self.warehouse_service.get_price_history_batch(tickers, date_range)

    def get_dividend_history_batch(self, tickers: List[Ticker], date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get dividend history for multiple tickers with warehouse caching."""
        if not self.warehouse_enabled:
            return self.yahoo_repo.get_dividend_history_batch(tickers, date_range)
        
        # Use warehouse service's optimized batch method
        return self.warehouse_service.get_dividend_history_batch(tickers, date_range)

    def reset_metrics(self):
        """Reset observability metrics."""
        self.warehouse_hits = 0
        self.warehouse_misses = 0
        self.yahoo_calls = 0
        self.missing_range_segments = 0
        self.calendar_skipped_days = 0
