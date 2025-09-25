"""
Parallel data fetcher service for efficient data retrieval.

This service provides parallel data fetching capabilities for warehouse
operations and external API calls while maintaining error isolation.
"""

import concurrent.futures
import threading
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass


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


class ParallelDataFetcher:
    """Service for managing parallel data fetching operations."""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize the parallel data fetcher service.
        
        Args:
            max_workers: Maximum number of worker threads. If None, uses optimal count.
        """
        
        # Determine optimal number of workers for I/O-bound operations
        if max_workers is None:
            import os
            # For I/O-bound operations, we can use more workers than CPU cores
            max_workers = min((os.cpu_count() or 4) * 4, 20)  # Cap at 20
        
        self.max_workers = max_workers
        self._thread_local = threading.local()
    
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
                    results.append(DataFetchResult(
                        task_id=task.task_id,
                        success=False,
                        error=f"Unexpected error: {str(e)}",
                        task_type=task.task_type
                    ))
        
        return results
    
    def _execute_single_fetch_task(self, task: DataFetchTask) -> DataFetchResult:
        """Execute a single data fetch task."""
        try:
            # Execute the fetch operation
            data = task.fetch_func(task.ticker, task.date_range)
            
            processing_time = 0.0
            
            return DataFetchResult(
                task_id=task.task_id,
                success=True,
                data=data,
                processing_time=processing_time,
                task_type=task.task_type
            )
            
        except Exception as e:
            processing_time = 0.0
            return DataFetchResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                processing_time=processing_time,
                task_type=task.task_type
            )
    


# Global instance
_parallel_data_fetcher: Optional[ParallelDataFetcher] = None


def get_parallel_data_fetcher() -> ParallelDataFetcher:
    """Get or create the global parallel data fetcher service instance."""
    global _parallel_data_fetcher
    if _parallel_data_fetcher is None:
        _parallel_data_fetcher = ParallelDataFetcher()
    return _parallel_data_fetcher
