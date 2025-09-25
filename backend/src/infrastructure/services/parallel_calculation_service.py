"""
Parallel calculation service for ticker analysis.

This service provides parallel processing capabilities for
financial calculations while maintaining error isolation and resource management.
"""

import concurrent.futures
import threading
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass


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


class ParallelCalculationService:
    """Service for parallel financial calculations."""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize the parallel calculation service.
        
        Args:
            max_workers: Maximum number of worker threads. If None, uses CPU count.
        """
        
        # Determine optimal number of workers
        if max_workers is None:
            import os
            max_workers = min(os.cpu_count() or 4, 20)  # Cap at 20 to avoid resource exhaustion
        
        self.max_workers = max_workers
        self._thread_local = threading.local()
    
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
        
        # Create calculation tasks
        tasks = []
        for i, ticker in enumerate(tickers):
            price_data = all_price_data.get(ticker)
            dividend_data = all_dividend_data.get(ticker)
            
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
                    results.append(CalculationResult(
                        task_id=task.task_id,
                        success=False,
                        error=f"Unexpected error: {str(e)}"
                    ))
        
        return results
    
    def _execute_single_task(self, task: CalculationTask) -> CalculationResult:
        """Execute a single calculation task."""
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
            
            processing_time = 0.0
            
            return CalculationResult(
                task_id=task.task_id,
                success=True,
                result=result,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = 0.0
            return CalculationResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    


# Global instance
_parallel_calculation_service: Optional[ParallelCalculationService] = None


def get_parallel_calculation_service() -> ParallelCalculationService:
    """Get or create the global parallel calculation service instance."""
    global _parallel_calculation_service
    if _parallel_calculation_service is None:
        _parallel_calculation_service = ParallelCalculationService()
    return _parallel_calculation_service
