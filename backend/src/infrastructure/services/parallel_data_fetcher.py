"""
Parallel data fetcher service for efficient data retrieval.

This service provides parallel data fetching capabilities for warehouse
operations and external API calls while maintaining error isolation.
"""

import concurrent.futures
import threading
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from ..logging.logger_service import get_logger_service
from ..logging.performance_monitor import get_monitor


@dataclass
class DataFetchTask:
    """Represents a single data fetch task."""
    task_id: str
    ticker: Any
    date_range: Any
    fetch_func: Callable
    task_type: str  # 'price', 'dividend', 'benchmark'


@dataclass
class DataFetchResult:
    """Represents the result of a data fetch task."""
    task_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    processing_time: float = 0.0
    task_type: str = ""


class DataFetcher:
    """Service for managing parallel data fetching operations."""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize the data fetcher service.
        
        Args:
            max_workers: Maximum number of worker threads. If None, uses optimal count.
        """
        self._logger = get_logger_service()
        self._monitor = get_monitor()
        
        # Determine optimal number of workers for I/O-bound operations
        if max_workers is None:
            import os
            # For I/O-bound operations, we can use more workers than CPU cores
            max_workers = min((os.cpu_count() or 4) * 4, 20)  # Cap at 20
        
        self.max_workers = max_workers
        self._thread_local = threading.local()
        
        self._logger.info(f"DataFetcher initialized with {max_workers} workers")
    
    def fetch_price_data_parallel(
        self, 
        tickers: List[Any],
        date_range: Any,
        fetch_func: Callable
    ) -> Tuple[Dict[Any, Any], List[str]]:
        """
        Fetch price data for multiple tickers in parallel.
        
        Args:
            tickers: List of ticker objects
            date_range: Date range for data fetching
            fetch_func: Function to use for fetching data
            
        Returns:
            Tuple of (data_by_ticker, failed_ticker_symbols)
        """
        self._logger.info(f"Starting parallel price data fetch for {len(tickers)} tickers")
        self._monitor.start_timing("parallel_price_fetch")
        
        # Create fetch tasks
        tasks = []
        for i, ticker in enumerate(tickers):
            task = DataFetchTask(
                task_id=f"price_{i}_{ticker.symbol}",
                ticker=ticker,
                date_range=date_range,
                fetch_func=fetch_func,
                task_type="price"
            )
            tasks.append(task)
        
        # Execute tasks in parallel
        results = self._execute_tasks_parallel(tasks)
        
        # Process results
        data_by_ticker = {}
        failed_tickers = []
        
        for result in results:
            if result.success:
                data_by_ticker[result.task_id.split('_', 2)[2]] = result.data  # Extract ticker symbol
            else:
                failed_tickers.append(result.task_id.split('_', 2)[2])
                self._logger.error(f"Price data fetch failed for {result.task_id}: {result.error}")
        
        fetch_time = self._performance_monitor.end_timing("parallel_price_fetch")
        
        # Log performance metrics
        success_rate = (len(data_by_ticker) / len(tickers)) * 100 if tickers else 0
        avg_time_per_ticker = fetch_time / len(tickers) if tickers else 0
        
        self._logger.info(f"Parallel price data fetch completed:")
        self._logger.info(f"  Total tickers: {len(tickers)}")
        self._logger.info(f"  Successful: {len(data_by_ticker)} ({success_rate:.1f}%)")
        self._logger.info(f"  Failed: {len(failed_tickers)}")
        self._logger.info(f"  Total time: {fetch_time:.3f}s")
        self._logger.info(f"  Average per ticker: {avg_time_per_ticker:.3f}s")
        
        return data_by_ticker, failed_tickers
    
    def fetch_dividend_data_parallel(
        self, 
        tickers: List[Any],
        date_range: Any,
        fetch_func: Callable
    ) -> Tuple[Dict[Any, Any], List[str]]:
        """
        Fetch dividend data for multiple tickers in parallel.
        
        Args:
            tickers: List of ticker objects
            date_range: Date range for data fetching
            fetch_func: Function to use for fetching data
            
        Returns:
            Tuple of (data_by_ticker, failed_ticker_symbols)
        """
        self._logger.info(f"Starting parallel dividend data fetch for {len(tickers)} tickers")
        self._monitor.start_timing("parallel_dividend_fetch")
        
        # Create fetch tasks
        tasks = []
        for i, ticker in enumerate(tickers):
            task = DataFetchTask(
                task_id=f"dividend_{i}_{ticker.symbol}",
                ticker=ticker,
                date_range=date_range,
                fetch_func=fetch_func,
                task_type="dividend"
            )
            tasks.append(task)
        
        # Execute tasks in parallel
        results = self._execute_tasks_parallel(tasks)
        
        # Process results
        data_by_ticker = {}
        failed_tickers = []
        
        for result in results:
            if result.success:
                data_by_ticker[result.task_id.split('_', 2)[2]] = result.data  # Extract ticker symbol
            else:
                failed_tickers.append(result.task_id.split('_', 2)[2])
                self._logger.error(f"Dividend data fetch failed for {result.task_id}: {result.error}")
        
        fetch_time = self._performance_monitor.end_timing("parallel_dividend_fetch")
        
        # Log performance metrics
        success_rate = (len(data_by_ticker) / len(tickers)) * 100 if tickers else 0
        avg_time_per_ticker = fetch_time / len(tickers) if tickers else 0
        
        self._logger.info(f"Parallel dividend data fetch completed:")
        self._logger.info(f"  Total tickers: {len(tickers)}")
        self._logger.info(f"  Successful: {len(data_by_ticker)} ({success_rate:.1f}%)")
        self._logger.info(f"  Failed: {len(failed_tickers)}")
        self._logger.info(f"  Total time: {fetch_time:.3f}s")
        self._logger.info(f"  Average per ticker: {avg_time_per_ticker:.3f}s")
        
        return data_by_ticker, failed_tickers
    
    def _execute_tasks_parallel(self, tasks: List[DataFetchTask]) -> List[DataFetchResult]:
        """Execute data fetch tasks in parallel using ThreadPoolExecutor."""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_single_fetch_task, task): task 
                for task in tasks
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self._logger.error(f"Unexpected error in fetch task {task.task_id}: {str(e)}")
                    results.append(DataFetchResult(
                        task_id=task.task_id,
                        success=False,
                        error=f"Unexpected error: {str(e)}",
                        task_type=task.task_type
                    ))
        
        return results
    
    def _execute_single_fetch_task(self, task: DataFetchTask) -> DataFetchResult:
        """Execute a single data fetch task."""
        start_time = self._performance_monitor.start_timing(f"fetch_{task.task_id}")
        
        try:
            # Execute the fetch operation
            data = task.fetch_func(task.ticker, task.date_range)
            
            processing_time = self._performance_monitor.end_timing(f"fetch_{task.task_id}")
            
            return DataFetchResult(
                task_id=task.task_id,
                success=True,
                data=data,
                processing_time=processing_time,
                task_type=task.task_type
            )
            
        except Exception as e:
            processing_time = self._performance_monitor.end_timing(f"fetch_{task.task_id}")
            return DataFetchResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                processing_time=processing_time,
                task_type=task.task_type
            )
    
    def get_optimal_worker_count(self, task_count: int) -> int:
        """
        Calculate optimal number of workers for given task count.
        
        Args:
            task_count: Number of tasks to execute
            
        Returns:
            Optimal number of workers
        """
        # For I/O-bound tasks, more workers than CPU cores can be beneficial
        import os
        cpu_count = os.cpu_count() or 4
        
        if task_count <= cpu_count:
            return task_count
        elif task_count <= cpu_count * 2:
            return min(task_count, cpu_count * 2)
        else:
            return min(cpu_count * 4, self.max_workers)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the parallel data fetcher service."""
        return {
            "max_workers": self.max_workers,
            "active_timings": self._monitor.get_active_timings(),
            "service_type": "parallel_data_fetcher"
        }


# Global instance
_data_fetcher: Optional[DataFetcher] = None


def get_data_fetcher() -> DataFetcher:
    """Get or create the global data fetcher service instance."""
    global _data_fetcher
    if _data_fetcher is None:
        _data_fetcher = DataFetcher()
    return _data_fetcher
