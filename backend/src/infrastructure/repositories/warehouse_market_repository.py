import pandas as pd
from typing import List, Dict
from ...application.interfaces.repositories import MarketDataRepository
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money
from ..warehouse.warehouse_service import WarehouseService
from ..warehouse.trading_day_service import TradingDayService
from ..logging.logger_service import get_logger_service
from ..logging.decorators import log_operation
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
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("infrastructure")
        
        # Observability counters
        self.warehouse_hits = 0
        self.warehouse_misses = 0
        self.yahoo_calls = 0
        self.missing_range_segments = 0
        self.calendar_skipped_days = 0
    
    @log_operation("warehouse_market", include_args=True, include_result=True)
    def get_price_history(self, tickers: List[Ticker], 
                         date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get historical price data with warehouse caching and batching."""
        if not self.warehouse_enabled:
            self._logger.info("Warehouse disabled, using direct Yahoo Finance")
            return self.yahoo_repo.get_price_history(tickers, date_range)
        
        self._logger.info(f"Warehouse-enabled price history fetch for {len(tickers)} tickers")
        self._logger.info(f"Date range: {date_range.start} to {date_range.end}")
        
        result = {}
        
        # Process tickers in batches for better performance
        batch_size = min(20, len(tickers))  # Process up to 20 tickers at once
        ticker_batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
        
        for batch_idx, ticker_batch in enumerate(ticker_batches):
            self._logger.info(f"Processing batch {batch_idx + 1}/{len(ticker_batches)} ({len(ticker_batch)} tickers)")
            
            # Log progress for large portfolios
            if len(tickers) > 50:
                progress_pct = ((batch_idx + 1) / len(ticker_batches)) * 100
                print(f"Warehouse Progress: Batch {batch_idx + 1}/{len(ticker_batches)} ({progress_pct:.1f}%)")
            
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
                    self._logger.error(f"Error processing ticker {ticker.symbol}: {str(e)}")
                    batch_missing_tickers.append(ticker)
            
            # Fetch missing data from Yahoo in batch
            if batch_missing_tickers:
                self._logger.info(f"Fetching {len(batch_missing_tickers)} missing tickers from Yahoo")
                try:
                    yahoo_result = self.yahoo_repo.get_price_history(batch_missing_tickers, date_range)
                    for ticker in batch_missing_tickers:
                        if ticker in yahoo_result and not yahoo_result[ticker].empty:
                            batch_warehouse_data[ticker] = yahoo_result[ticker]
                            # Store in warehouse for future use
                            self.warehouse_service.store_price_data(ticker, yahoo_result[ticker])
                except Exception as yahoo_error:
                    self._logger.error(f"Yahoo batch fetch failed: {str(yahoo_error)}")
            
            # Add batch results to final result
            result.update(batch_warehouse_data)
        
        self._logger.info(f"Warehouse processing completed: {len(result)} tickers processed")
        return result
    
    def _get_ticker_price_history(self, ticker: Ticker, date_range: DateRange) -> pd.Series:
        """Get price history for a single ticker with warehouse caching."""
        self._logger.debug(f"Processing ticker {ticker.symbol}")
        
        # Step 1: Check warehouse coverage
        coverage = self.warehouse_service.get_coverage(ticker, date_range)
        
        # Step 2: Determine trading days in the requested range
        potential_trading_days = self.trading_day_service.get_trading_days_in_range(date_range)
        
        # Step 3: Check if we have sufficient coverage
        # We need to be smarter about this - we should check if we have data for
        # the actual trading days that exist in the market, not just potential trading days
        
        # First, try to get data from warehouse to see what we have
        existing_data = self.warehouse_service.get_price_data(ticker, date_range)
        
        if not existing_data.empty:
            # We have some data in warehouse, check if it covers the requested range adequately
            existing_dates = {date.strftime('%Y-%m-%d') for date in existing_data.index}
            
            # If we have data for most of the potential trading days (allowing for holidays),
            # and the data spans the requested range, use the warehouse
            coverage_ratio = len(existing_dates.intersection(potential_trading_days)) / len(potential_trading_days)
            
            if coverage_ratio >= 0.8:  # At least 80% coverage
                self._logger.debug(f"Sufficient data available in warehouse for {ticker.symbol} (coverage: {coverage_ratio:.1%})")
                self.warehouse_hits += 1
                missing_ranges = []  # No missing ranges needed
            else:
                # Calculate missing ranges using potential trading days
                missing_ranges = self.warehouse_service.get_missing_ranges(
                    ticker, date_range, potential_trading_days
                )
        else:
            # No data in warehouse, calculate missing ranges
            missing_ranges = self.warehouse_service.get_missing_ranges(
                ticker, date_range, potential_trading_days
            )
        
        if missing_ranges:
            self._logger.info(f"Found {len(missing_ranges)} missing ranges for {ticker.symbol}: {missing_ranges}")
            self.warehouse_misses += 1
            self.missing_range_segments += len(missing_ranges)
            
            # Step 5: Fetch missing data from Yahoo - batch multiple ranges into single call
            if len(missing_ranges) > 1:
                # If multiple ranges, try to batch them into a single call
                min_date = min(start for start, end in missing_ranges)
                max_date = max(end for start, end in missing_ranges)
                
                self._logger.info(f"Batching {len(missing_ranges)} ranges into single call: {min_date} to {max_date}")
                
                # Create date range for the entire missing period
                missing_range = DateRange(min_date, max_date)
                
                # Fetch from Yahoo
                yahoo_data = self.yahoo_repo.get_price_history([ticker], missing_range)
                self.yahoo_calls += 1
                self._logger.info(f"Yahoo call {self.yahoo_calls} completed for batched range {min_date} to {max_date}")
                
                if ticker in yahoo_data and not yahoo_data[ticker].empty:
                    # Store in warehouse
                    self.warehouse_service.store_price_data(ticker, yahoo_data[ticker])
                    self._logger.info(f"Stored {len(yahoo_data[ticker])} data points for {ticker.symbol} from batched range")
                else:
                    self._logger.warning(f"No data returned from Yahoo for {ticker.symbol} in batched range {min_date} to {max_date}")
            else:
                # Single range - use original logic
                start_date, end_date = missing_ranges[0]
                self._logger.info(f"Fetching missing data for {ticker.symbol}: {start_date} to {end_date}")
                
                # Create date range for this missing segment
                missing_range = DateRange(start_date, end_date)
                
                # Fetch from Yahoo
                yahoo_data = self.yahoo_repo.get_price_history([ticker], missing_range)
                self.yahoo_calls += 1
                self._logger.info(f"Yahoo call {self.yahoo_calls} completed for range {start_date} to {end_date}")
                
                if ticker in yahoo_data and not yahoo_data[ticker].empty:
                    # Store in warehouse
                    self.warehouse_service.store_price_data(ticker, yahoo_data[ticker])
                    self._logger.info(f"Stored {len(yahoo_data[ticker])} data points for {ticker.symbol} from {start_date} to {end_date}")
                else:
                    self._logger.warning(f"No data returned from Yahoo for {ticker.symbol} in range {start_date} to {end_date}")
        
        # Step 6: Read complete requested range from warehouse
        final_data = self.warehouse_service.get_price_data(ticker, date_range)
        
        if final_data.empty:
            self._logger.warning(f"No data available for {ticker.symbol} after warehouse processing")
        
        return final_data
    
    @log_operation("warehouse_market", include_args=True, include_result=True)
    def get_current_prices(self, tickers: List[Ticker]) -> Dict[Ticker, Money]:
        """Get current prices - always use Yahoo for real-time data."""
        self._logger.info("Getting current prices from Yahoo Finance (real-time data)")
        return self.yahoo_repo.get_current_prices(tickers)
    
    @log_operation("warehouse_market", include_args=True, include_result=True)
    def get_benchmark_data(self, benchmark_symbol: str, 
                          date_range: DateRange) -> pd.Series:
        """Get benchmark data (e.g., S&P 500) for Beta calculation with warehouse caching."""
        if not self.warehouse_enabled:
            self._logger.info(f"Getting benchmark data for {benchmark_symbol} from Yahoo Finance (warehouse disabled)")
            return self.yahoo_repo.get_benchmark_data(benchmark_symbol, date_range)
        
        # Check if we have benchmark coverage information in warehouse
        if self.warehouse_service.has_benchmark_coverage(benchmark_symbol, date_range):
            # We have coverage information, get the actual data
            existing_benchmark = self.warehouse_service.get_benchmark_data(benchmark_symbol, date_range)
            self._logger.debug(f"Using cached benchmark data for {benchmark_symbol} from warehouse")
            self.warehouse_hits += 1
            return existing_benchmark
        
        # No coverage information in warehouse, fetch from Yahoo and store
        self._logger.info(f"Fetching benchmark data for {benchmark_symbol} from Yahoo Finance")
        benchmark_data = self.yahoo_repo.get_benchmark_data(benchmark_symbol, date_range)
        
        # Store in warehouse for future use (including coverage information)
        self.warehouse_service.store_benchmark_data(benchmark_symbol, benchmark_data, date_range)
        if not benchmark_data.empty:
            self._logger.debug(f"Stored benchmark data for {benchmark_symbol} in warehouse")
        else:
            self._logger.debug(f"Stored benchmark absence information for {benchmark_symbol} in warehouse")
        
        self.warehouse_misses += 1
        return benchmark_data
    
    @log_operation("warehouse_market", include_args=True, include_result=True)
    def get_dividend_history(self, ticker: Ticker, 
                           date_range: DateRange) -> pd.Series:
        """Get dividend history with warehouse caching."""
        if not self.warehouse_enabled:
            self._logger.info(f"Getting dividend history for {ticker.symbol} from Yahoo Finance (warehouse disabled)")
            return self.yahoo_repo.get_dividend_history(ticker, date_range)
        
        # Check if we have dividend coverage information in warehouse
        if self.warehouse_service.has_dividend_coverage(ticker, date_range):
            # We have coverage information, get the actual data
            existing_dividends = self.warehouse_service.get_dividend_data(ticker, date_range)
            self._logger.debug(f"Using cached dividend data for {ticker.symbol} from warehouse")
            self.warehouse_hits += 1
            return existing_dividends
        
        # No coverage information in warehouse, fetch from Yahoo and store
        self._logger.info(f"Fetching dividend history for {ticker.symbol} from Yahoo Finance")
        dividend_data = self.yahoo_repo.get_dividend_history(ticker, date_range)
        
        # Store in warehouse for future use (including coverage information)
        self.warehouse_service.store_dividend_data(ticker, dividend_data, date_range)
        if not dividend_data.empty:
            self._logger.debug(f"Stored dividend data for {ticker.symbol} in warehouse")
        else:
            self._logger.debug(f"Stored dividend absence information for {ticker.symbol} in warehouse")
        
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
    
    def reset_metrics(self):
        """Reset observability metrics."""
        self.warehouse_hits = 0
        self.warehouse_misses = 0
        self.yahoo_calls = 0
        self.missing_range_segments = 0
        self.calendar_skipped_days = 0
