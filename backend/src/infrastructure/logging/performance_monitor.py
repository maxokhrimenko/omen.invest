"""
Performance monitoring utilities for timing and analysis.
"""

import time
from typing import Dict, Optional
from ..logging.logger_service import get_logger_service


class PerformanceMonitor:
    """Performance monitoring service for timing and analysis."""
    
    def __init__(self):
        self._timings: Dict[str, float] = {}
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("performance")
        self._logger.info("PerformanceMonitor initialized")
    
    def start_timing(self, operation: str) -> None:
        """Start timing an operation."""
        self._timings[operation] = time.time()
        self._logger.debug(f"Started timing: {operation}")
    
    def end_timing(self, operation: str) -> float:
        """End timing an operation and return duration in seconds."""
        if operation in self._timings:
            duration = time.time() - self._timings[operation]
            del self._timings[operation]
            self._logger.info(f"{operation}: {duration:.3f}s")
            return duration
        else:
            self._logger.warning(f"Attempted to end timing for unknown operation: {operation}")
            return 0.0
    
    def log_batch_performance(self, ticker_count: int, total_time: float, 
                            price_fetch_time: float, dividend_fetch_time: float,
                            benchmark_fetch_time: float, calculation_time: float) -> None:
        """Log detailed batch performance metrics."""
        self._logger.info(f"BATCH PERFORMANCE - {ticker_count} tickers in {total_time:.3f}s")
        self._logger.info(f"  Price data fetch: {price_fetch_time:.3f}s")
        self._logger.info(f"  Dividend data fetch: {dividend_fetch_time:.3f}s")
        self._logger.info(f"  Benchmark data fetch: {benchmark_fetch_time:.3f}s")
        self._logger.info(f"  Calculations: {calculation_time:.3f}s")
        self._logger.info(f"  Average per ticker: {total_time/ticker_count:.3f}s")
        
        # Calculate efficiency metrics
        data_fetch_time = price_fetch_time + dividend_fetch_time + benchmark_fetch_time
        data_fetch_percentage = (data_fetch_time / total_time) * 100 if total_time > 0 else 0
        calculation_percentage = (calculation_time / total_time) * 100 if total_time > 0 else 0
        
        self._logger.info(f"  Data fetch: {data_fetch_percentage:.1f}% of total time")
        self._logger.info(f"  Calculations: {calculation_percentage:.1f}% of total time")
    
    def log_individual_performance(self, ticker_symbol: str, total_time: float,
                                 price_fetch_time: float, dividend_fetch_time: float,
                                 benchmark_fetch_time: float, calculation_time: float) -> None:
        """Log detailed individual ticker performance metrics."""
        self._logger.debug(f"TICKER PERFORMANCE - {ticker_symbol} in {total_time:.3f}s")
        self._logger.debug(f"  Price data fetch: {price_fetch_time:.3f}s")
        self._logger.debug(f"  Dividend data fetch: {dividend_fetch_time:.3f}s")
        self._logger.debug(f"  Benchmark data fetch: {benchmark_fetch_time:.3f}s")
        self._logger.debug(f"  Calculations: {calculation_time:.3f}s")
    
    def get_active_timings(self) -> Dict[str, float]:
        """Get currently active timings."""
        return self._timings.copy()
    
    def clear_timings(self) -> None:
        """Clear all active timings."""
        self._timings.clear()
        self._logger.debug("Cleared all active timings")
    
    def log_performance_summary(self, operation: str, ticker_count: int, 
                              total_time: float, success_count: int, failed_count: int) -> None:
        """Log a performance summary for an operation."""
        success_rate = (success_count / ticker_count) * 100 if ticker_count > 0 else 0
        avg_time_per_ticker = total_time / ticker_count if ticker_count > 0 else 0
        
        self._logger.info(f"PERFORMANCE SUMMARY - {operation}")
        self._logger.info(f"  Total tickers: {ticker_count}")
        self._logger.info(f"  Successful: {success_count} ({success_rate:.1f}%)")
        self._logger.info(f"  Failed: {failed_count}")
        self._logger.info(f"  Total time: {total_time:.3f}s")
        self._logger.info(f"  Average per ticker: {avg_time_per_ticker:.3f}s")
        
        if ticker_count > 0:
            if avg_time_per_ticker < 0.1:
                self._logger.info(f"  Performance: EXCELLENT (< 0.1s per ticker)")
            elif avg_time_per_ticker < 0.5:
                self._logger.info(f"  Performance: GOOD (< 0.5s per ticker)")
            elif avg_time_per_ticker < 1.0:
                self._logger.info(f"  Performance: ACCEPTABLE (< 1.0s per ticker)")
            else:
                self._logger.warning(f"  Performance: SLOW (> 1.0s per ticker)")


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
