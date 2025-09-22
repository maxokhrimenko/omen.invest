"""
Parallel calculation service for efficient ticker analysis.

This service provides parallel processing capabilities for CPU-intensive
financial calculations while maintaining error isolation and resource management.
"""

import concurrent.futures
import threading
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass
from ..logging.logger_service import get_logger_service
from ..logging.performance_monitor import get_monitor


@dataclass
class CalculationTask:
    """Represents a single calculation task."""
    task_id: str
    ticker: Any
    price_data: Any
    dividend_data: Any
    risk_free_rate: float
    date_range: Any
    benchmark_data: Any
    calculation_func: Callable


@dataclass
class CalculationResult:
    """Represents the result of a calculation task."""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    processing_time: float = 0.0


class CalculationService:
    """Service for managing parallel financial calculations."""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize the calculation service.
        
        Args:
            max_workers: Maximum number of worker threads. If None, uses CPU count.
        """
        self._logger = get_logger_service()
        self._monitor = get_monitor()
        
        # Determine optimal number of workers
        if max_workers is None:
            import os
            max_workers = min(os.cpu_count() or 4, 20)  # Cap at 20 to avoid resource exhaustion
        
        self.max_workers = max_workers
        self._thread_local = threading.local()
        
        self._logger.info(f"CalculationService initialized with {max_workers} workers")
    
    def calculate_ticker_metrics_parallel(
        self, 
        tickers: List[Any],
        all_price_data: Dict[Any, Any],
        all_dividend_data: Dict[Any, Any],
        risk_free_rate: float,
        date_range: Any,
        benchmark_data: Any,
        calculation_func: Callable
    ) -> Tuple[List[Any], List[str]]:
        """
        Calculate ticker metrics in parallel.
        
        Args:
            tickers: List of ticker objects
            all_price_data: Dictionary of price data by ticker
            all_dividend_data: Dictionary of dividend data by ticker
            risk_free_rate: Risk-free rate for calculations
            date_range: Date range for calculations
            benchmark_data: Benchmark data for calculations
            calculation_func: Function to use for calculations
            
        Returns:
            Tuple of (successful_metrics, failed_ticker_symbols)
        """
        self._logger.info(f"Starting parallel calculation for {len(tickers)} tickers")
        self._monitor.start_timing("parallel_calculations")
        
        # Create calculation tasks
        tasks = []
        for i, ticker in enumerate(tickers):
            price_data = all_price_data.get(ticker)
            dividend_data = all_dividend_data.get(ticker)
            
            # Debug logging
            self._logger.info(f"Task {i} - {ticker.symbol}:")
            self._logger.info(f"  Price data type: {type(price_data)}")
            self._logger.info(f"  Price data empty: {price_data.empty if hasattr(price_data, 'empty') else 'N/A'}")
            self._logger.info(f"  Dividend data type: {type(dividend_data)}")
            self._logger.info(f"  Dividend data empty: {dividend_data.empty if hasattr(dividend_data, 'empty') else 'N/A'}")
            
            task = CalculationTask(
                task_id=f"ticker_{i}_{ticker.symbol}",
                ticker=ticker,
                price_data=price_data,
                dividend_data=dividend_data,
                risk_free_rate=risk_free_rate,
                date_range=date_range,
                benchmark_data=benchmark_data,
                calculation_func=calculation_func
            )
            tasks.append(task)
        
        # Execute tasks in parallel
        results = self._execute_tasks_parallel(tasks)
        
        # Process results
        successful_metrics = []
        failed_tickers = []
        
        for result in results:
            if result.success:
                successful_metrics.append(result.result)
            else:
                failed_tickers.append(result.task_id.split('_', 2)[2])  # Extract ticker symbol
                self._logger.error(f"Calculation failed for {result.task_id}: {result.error}")
        
        calculation_time = self._monitor.end_timing("parallel_calculations")
        
        # Log performance metrics
        success_rate = (len(successful_metrics) / len(tickers)) * 100 if tickers else 0
        avg_time_per_ticker = calculation_time / len(tickers) if tickers else 0
        
        self._logger.info(f"Parallel calculation completed:")
        self._logger.info(f"  Total tickers: {len(tickers)}")
        self._logger.info(f"  Successful: {len(successful_metrics)} ({success_rate:.1f}%)")
        self._logger.info(f"  Failed: {len(failed_tickers)}")
        self._logger.info(f"  Total time: {calculation_time:.3f}s")
        self._logger.info(f"  Average per ticker: {avg_time_per_ticker:.3f}s")
        self._logger.info(f"  Workers used: {self.max_workers}")
        
        return successful_metrics, failed_tickers
    
    def _execute_tasks_parallel(self, tasks: List[CalculationTask]) -> List[CalculationResult]:
        """Execute calculation tasks in parallel using ThreadPoolExecutor."""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_single_task, task): task 
                for task in tasks
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self._logger.error(f"Unexpected error in task {task.task_id}: {str(e)}")
                    results.append(CalculationResult(
                        task_id=task.task_id,
                        success=False,
                        error=f"Unexpected error: {str(e)}"
                    ))
        
        return results
    
    def _execute_single_task(self, task: CalculationTask) -> CalculationResult:
        """Execute a single calculation task."""
        start_time = self._monitor.start_timing(f"task_{task.task_id}")
        
        try:
            # Validate input data
            if task.price_data is None or task.price_data.empty or len(task.price_data) < 2:
                return CalculationResult(
                    task_id=task.task_id,
                    success=False,
                    error="Insufficient price data",
                    processing_time=0.0
                )
            
            # Execute the calculation
            result = task.calculation_func(
                task.ticker,
                task.price_data,
                task.dividend_data,
                task.risk_free_rate,
                task.date_range,
                task.benchmark_data
            )
            
            processing_time = self._monitor.end_timing(f"task_{task.task_id}")
            
            return CalculationResult(
                task_id=task.task_id,
                success=True,
                result=result,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = self._monitor.end_timing(f"task_{task.task_id}")
            return CalculationResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    def get_optimal_worker_count(self, task_count: int) -> int:
        """
        Calculate optimal number of workers for given task count.
        
        Args:
            task_count: Number of tasks to execute
            
        Returns:
            Optimal number of workers
        """
        # For CPU-bound tasks, more workers than CPU cores can be counterproductive
        # For I/O-bound tasks, more workers can be beneficial
        # Financial calculations are mostly CPU-bound with some I/O
        
        import os
        cpu_count = os.cpu_count() or 4
        
        if task_count <= cpu_count:
            return task_count
        elif task_count <= cpu_count * 2:
            return min(task_count, cpu_count)
        else:
            return min(cpu_count * 2, self.max_workers)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the parallel calculation service."""
        return {
            "max_workers": self.max_workers,
            "active_timings": self._monitor.get_active_timings(),
            "service_type": "parallel_calculation"
        }


# Global instance
_calculation_service: Optional[CalculationService] = None


def get_calculation_service() -> CalculationService:
    """Get or create the global calculation service instance."""
    global _calculation_service
    if _calculation_service is None:
        _calculation_service = CalculationService()
    return _calculation_service
