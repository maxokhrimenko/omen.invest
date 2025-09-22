"""
Performance benchmark script for portfolio analysis optimizations.

This script compares the performance of the original sequential implementation
with the new parallel implementation to measure improvements.
"""

import time
import sys
import os
import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.domain.entities.ticker import Ticker
from src.domain.value_objects.date_range import DateRange
from src.application.use_cases.analyze_ticker import AnalyzeTickerUseCase, AnalyzeTickersRequest
from src.infrastructure.repositories.warehouse_market_repository import WarehouseMarketRepository
from src.infrastructure.logging.logger_service import initialize_logging


@dataclass
class BenchmarkResult:
    """Results of a performance benchmark."""
    test_name: str
    ticker_count: int
    execution_time: float
    success_count: int
    failed_count: int
    memory_usage_mb: float
    throughput_tickers_per_second: float


class PerformanceBenchmark:
    """Performance benchmark for portfolio analysis optimizations."""
    
    def __init__(self):
        self.logger_service = initialize_logging("logs/benchmark")
        self.logger = self.logger_service.get_logger("benchmark")
        
        # Initialize repositories
        self.market_repo = WarehouseMarketRepository(warehouse_enabled=True)
        self.analyze_ticker_use_case = AnalyzeTickerUseCase(self.market_repo)
        
        # Test data
        self.test_tickers = [
            Ticker("AAPL"), Ticker("MSFT"), Ticker("GOOGL"), Ticker("AMZN"), Ticker("TSLA"),
            Ticker("META"), Ticker("NVDA"), Ticker("NFLX"), Ticker("ADBE"), Ticker("CRM"),
            Ticker("ORCL"), Ticker("INTC"), Ticker("AMD"), Ticker("QCOM"), Ticker("AVGO"),
            Ticker("TXN"), Ticker("MU"), Ticker("AMAT"), Ticker("LRCX"), Ticker("KLAC"),
            Ticker("MCHP"), Ticker("ADI"), Ticker("MRVL"), Ticker("SWKS"), Ticker("QRVO"),
            Ticker("SLAB"), Ticker("MXL"), Ticker("CRUS"), Ticker("SYNA"), Ticker("OLED"),
            Ticker("PKG"), Ticker("SEE"), Ticker("EMN"), Ticker("DOW"), Ticker("DD"),
            Ticker("PPG"), Ticker("SHW"), Ticker("ECL"), Ticker("APD"), Ticker("LIN"),
            Ticker("NOC"), Ticker("LMT"), Ticker("RTX"), Ticker("GD"), Ticker("BA"),
            Ticker("HON"), Ticker("GE"), Ticker("CAT"), Ticker("DE"), Ticker("CMI")
        ]
        
        self.date_range = DateRange("2023-01-01", "2024-01-01")
    
    def run_benchmark(self, ticker_count: int, iterations: int = 3) -> BenchmarkResult:
        """Run benchmark for specified number of tickers."""
        self.logger.info(f"Running benchmark for {ticker_count} tickers, {iterations} iterations")
        
        # Select test tickers
        test_tickers = self.test_tickers[:ticker_count]
        
        # Run multiple iterations and take average
        execution_times = []
        success_counts = []
        failed_counts = []
        memory_usages = []
        
        for i in range(iterations):
            self.logger.info(f"Running iteration {i+1}/{iterations}")
            
            # Measure memory before
            import psutil
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Run the test
            start_time = time.time()
            
            request = AnalyzeTickersRequest(
                tickers=test_tickers,
                date_range=self.date_range,
                risk_free_rate=0.03
            )
            
            response = self.analyze_ticker_use_case.execute_batch(request)
            
            end_time = time.time()
            
            # Measure memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            execution_times.append(end_time - start_time)
            success_counts.append(len(response.ticker_metrics))
            failed_counts.append(len(response.failed_tickers))
            memory_usages.append(memory_after - memory_before)
            
            self.logger.info(f"Iteration {i+1} completed in {execution_times[-1]:.3f}s")
        
        # Calculate averages
        avg_execution_time = sum(execution_times) / len(execution_times)
        avg_success_count = sum(success_counts) / len(success_counts)
        avg_failed_count = sum(failed_counts) / len(failed_counts)
        avg_memory_usage = sum(memory_usages) / len(memory_usages)
        throughput = ticker_count / avg_execution_time
        
        result = BenchmarkResult(
            test_name=f"Parallel Analysis ({ticker_count} tickers)",
            ticker_count=ticker_count,
            execution_time=avg_execution_time,
            success_count=int(avg_success_count),
            failed_count=int(avg_failed_count),
            memory_usage_mb=avg_memory_usage,
            throughput_tickers_per_second=throughput
        )
        
        self.logger.info(f"Benchmark completed: {result}")
        return result
    
    def run_scalability_test(self, ticker_counts: List[int]) -> List[BenchmarkResult]:
        """Run scalability test with different ticker counts."""
        self.logger.info(f"Running scalability test with ticker counts: {ticker_counts}")
        
        results = []
        for ticker_count in ticker_counts:
            try:
                result = self.run_benchmark(ticker_count, iterations=2)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Benchmark failed for {ticker_count} tickers: {str(e)}")
                continue
        
        return results
    
    def generate_report(self, results: List[BenchmarkResult]) -> str:
        """Generate a performance report."""
        report = []
        report.append("=" * 80)
        report.append("PORTFOLIO ANALYSIS PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary table
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 40)
        report.append(f"{'Tickers':<10} {'Time (s)':<12} {'Success':<10} {'Failed':<10} {'Memory (MB)':<12} {'Throughput':<15}")
        report.append("-" * 40)
        
        for result in results:
            report.append(
                f"{result.ticker_count:<10} "
                f"{result.execution_time:<12.3f} "
                f"{result.success_count:<10} "
                f"{result.failed_count:<10} "
                f"{result.memory_usage_mb:<12.2f} "
                f"{result.throughput_tickers_per_second:<15.2f}"
            )
        
        report.append("")
        
        # Performance analysis
        if len(results) >= 2:
            report.append("PERFORMANCE ANALYSIS")
            report.append("-" * 40)
            
            # Calculate scaling efficiency
            base_result = results[0]
            for result in results[1:]:
                expected_time = base_result.execution_time * (result.ticker_count / base_result.ticker_count)
                actual_time = result.execution_time
                efficiency = (expected_time / actual_time) * 100 if actual_time > 0 else 0
                
                report.append(f"Scaling from {base_result.ticker_count} to {result.ticker_count} tickers:")
                report.append(f"  Expected time: {expected_time:.3f}s")
                report.append(f"  Actual time: {actual_time:.3f}s")
                report.append(f"  Scaling efficiency: {efficiency:.1f}%")
                report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 40)
        
        if results:
            avg_throughput = sum(r.throughput_tickers_per_second for r in results) / len(results)
            if avg_throughput > 10:
                report.append("✅ EXCELLENT: Throughput > 10 tickers/second")
            elif avg_throughput > 5:
                report.append("✅ GOOD: Throughput > 5 tickers/second")
            elif avg_throughput > 2:
                report.append("⚠️  FAIR: Throughput > 2 tickers/second")
            else:
                report.append("❌ POOR: Throughput < 2 tickers/second")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, results: List[BenchmarkResult], filename: str = "benchmark_results.txt"):
        """Save benchmark results to file."""
        report = self.generate_report(results)
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        with open(f"logs/{filename}", "w") as f:
            f.write(report)
        
        self.logger.info(f"Benchmark results saved to logs/{filename}")
    
    def run_full_benchmark(self):
        """Run a comprehensive benchmark suite."""
        self.logger.info("Starting comprehensive benchmark suite")
        
        # Test different ticker counts
        ticker_counts = [5, 10, 20, 50]
        
        # Run scalability test
        results = self.run_scalability_test(ticker_counts)
        
        # Generate and save report
        self.save_results(results)
        
        # Print summary
        print(self.generate_report(results))
        
        self.logger.info("Benchmark suite completed")


def main():
    """Main benchmark execution."""
    print("🚀 Starting Portfolio Analysis Performance Benchmark")
    print("=" * 60)
    
    try:
        benchmark = PerformanceBenchmark()
        benchmark.run_full_benchmark()
        print("\n✅ Benchmark completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Benchmark failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
