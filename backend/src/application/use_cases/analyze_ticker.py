from dataclasses import dataclass
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
import time
from ..interfaces.repositories import MarketDataRepository
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money
from ...domain.value_objects.percentage import Percentage
from ...infrastructure.logging.logger_service import get_logger_service
from ...infrastructure.logging.performance_monitor import get_performance_monitor
from ...infrastructure.services.parallel_calculation_service import get_parallel_calculation_service
from ...infrastructure.services.metrics_calculator import MetricsCalculator

@dataclass
class AnalyzeTickerRequest:
    ticker: Ticker
    date_range: DateRange
    risk_free_rate: float = 0.03

@dataclass
class TickerMetrics:
    ticker: Ticker
    total_return: Percentage
    annualized_return: Percentage
    volatility: Percentage
    sharpe_ratio: float
    max_drawdown: Percentage
    sortino_ratio: float
    beta: float
    var_95: Percentage
    momentum_12_1: Percentage
    dividend_yield: Percentage
    dividend_amount: Money
    dividend_frequency: str
    annualized_dividend: Money
    start_price: Money
    end_price: Money

@dataclass
class AnalyzeTickerResponse:
    metrics: Optional[TickerMetrics]
    success: bool
    message: str
    has_data_at_start: bool = True
    first_available_date: Optional[str] = None

@dataclass
class AnalyzeTickersRequest:
    tickers: List[Ticker]
    date_range: DateRange
    risk_free_rate: float = 0.03

@dataclass
class AnalyzeTickersResponse:
    ticker_metrics: List[TickerMetrics]
    failed_tickers: List[str]
    success: bool
    message: str
    processing_time_seconds: float
    missing_tickers: List[str] = None
    tickers_without_start_data: List[str] = None
    first_available_dates: Optional[Dict[str, str]] = None

class AnalyzeTickerUseCase:
    def __init__(self, market_data_repo: MarketDataRepository):
        self._market_data_repo = market_data_repo
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("application")
        self._performance_monitor = get_performance_monitor()
        self._parallel_calculation_service = get_parallel_calculation_service()
    
    def execute(self, request: AnalyzeTickerRequest) -> AnalyzeTickerResponse:
        try:
            # Get price history
            price_history = self._market_data_repo.get_price_history(
                [request.ticker],
                request.date_range
            )
            
            if not price_history or request.ticker not in price_history:
                return AnalyzeTickerResponse(
                    metrics=None,
                    success=False,
                    message=f"No price data available for {request.ticker.symbol}",
                    has_data_at_start=False
                )
            
            prices = price_history[request.ticker]
            if prices.empty or len(prices) < 2:
                return AnalyzeTickerResponse(
                    metrics=None,
                    success=False,
                    message=f"Insufficient price data for {request.ticker.symbol}",
                    has_data_at_start=False
                )
            
            # Check if data is available at start date (with tolerance for business days)
            start_timestamp = pd.Timestamp(request.date_range.start)
            first_available_date = prices.index[0]
            # Allow up to 5 business days tolerance for start date (to account for weekends/holidays)
            tolerance_days = 5
            max_allowed_start = start_timestamp + pd.Timedelta(days=tolerance_days)
            has_data_at_start = first_available_date <= max_allowed_start
            
            if not has_data_at_start:
                return AnalyzeTickerResponse(
                    metrics=None,
                    success=False,
                    message=f"No data available within {tolerance_days} days of start date {request.date_range.start} for {request.ticker.symbol}. First available data: {first_available_date.date()}",
                    has_data_at_start=False,
                    first_available_date=str(first_available_date.date())
                )
            
            # Get dividend history
            dividend_history = self._market_data_repo.get_dividend_history(
                request.ticker,
                request.date_range
            )
            
            # Get benchmark data for Beta calculation
            benchmark_data = self._market_data_repo.get_benchmark_data(
                "^GSPC",  # S&P 500 symbol
                request.date_range
            )
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                request.ticker,
                prices,
                dividend_history,
                request.risk_free_rate,
                request.date_range,
                benchmark_data
            )
            
            return AnalyzeTickerResponse(
                metrics=metrics,
                success=True,
                message=f"Analysis completed for {request.ticker.symbol}",
                has_data_at_start=True,
                first_available_date=str(first_available_date.date())
            )
            
        except Exception as e:
            return AnalyzeTickerResponse(
                metrics=None,
                success=False,
                message=f"Analysis failed for {request.ticker.symbol}: {str(e)}"
            )
    
    def execute_batch(self, request: AnalyzeTickersRequest) -> AnalyzeTickersResponse:
        """Execute multiple ticker analysis with smart batching and performance monitoring."""
        start_time = time.time()
        self._performance_monitor.start_timing("batch_analysis")
        
        try:
            self._logger.info(f"Starting batch analysis for {len(request.tickers)} tickers")
            self._logger.info(f"Date range: {request.date_range.start} to {request.date_range.end}")
            
            # Step 1: Batch fetch all data (3 calls instead of 3 * N calls)
            self._performance_monitor.start_timing("price_data_fetch")
            all_price_data = self._market_data_repo.get_price_history_batch(
                request.tickers, request.date_range
            )
            price_fetch_time = self._performance_monitor.end_timing("price_data_fetch")
            
            self._performance_monitor.start_timing("dividend_data_fetch")
            all_dividend_data = self._market_data_repo.get_dividend_history_batch(
                request.tickers, request.date_range
            )
            dividend_fetch_time = self._performance_monitor.end_timing("dividend_data_fetch")
            
            # Fetch benchmark data once (shared across all tickers)
            self._performance_monitor.start_timing("benchmark_data_fetch")
            benchmark_data = self._market_data_repo.get_benchmark_data(
                "^GSPC", request.date_range
            )
            benchmark_fetch_time = self._performance_monitor.end_timing("benchmark_data_fetch")
            
            # Step 2: Analyze data availability and categorize tickers
            self._performance_monitor.start_timing("calculations")
            
            # Categorize tickers based on data availability
            missing_tickers = []
            tickers_without_start_data = []
            first_available_dates = {}
            
            for ticker in request.tickers:
                if ticker not in all_price_data or all_price_data[ticker].empty:
                    missing_tickers.append(ticker.symbol)
                else:
                    # Check if data is available at start date
                    prices = all_price_data[ticker]
                    start_timestamp = pd.Timestamp(request.date_range.start)
                    first_available_date = prices.index[0]
                    
                    # Allow up to 5 business days tolerance for start date
                    tolerance_days = 5
                    max_allowed_start = start_timestamp + pd.Timedelta(days=tolerance_days)
                    
                    if first_available_date > max_allowed_start:
                        tickers_without_start_data.append(ticker.symbol)
                        first_available_dates[ticker.symbol] = first_available_date.strftime('%Y-%m-%d')
            
            # Use parallel calculation service for better performance
            ticker_metrics, failed_tickers = self._parallel_calculation_service.calculate_ticker_metrics_parallel(
                tickers=request.tickers,
                all_price_data=all_price_data,
                all_dividend_data=all_dividend_data,
                risk_free_rate=request.risk_free_rate,
                date_range=request.date_range,
                benchmark_data=benchmark_data,
                calculation_func=lambda ticker, prices, dividends, risk_free_rate, date_range, benchmark_data: self._calculate_metrics(ticker, prices, dividends, risk_free_rate, date_range, benchmark_data)
            )
            
            calculation_time = self._performance_monitor.end_timing("calculations")
            total_time = self._performance_monitor.end_timing("batch_analysis")
            
            # Log detailed performance metrics
            self._performance_monitor.log_batch_performance(
                ticker_count=len(request.tickers),
                total_time=total_time,
                price_fetch_time=price_fetch_time,
                dividend_fetch_time=dividend_fetch_time,
                benchmark_fetch_time=benchmark_fetch_time,
                calculation_time=calculation_time
            )
            
            # Log performance summary
            self._performance_monitor.log_performance_summary(
                operation="batch_ticker_analysis",
                ticker_count=len(request.tickers),
                total_time=total_time,
                success_count=len(ticker_metrics),
                failed_count=len(failed_tickers)
            )
            
            return AnalyzeTickersResponse(
                ticker_metrics=ticker_metrics,
                failed_tickers=failed_tickers,
                success=True,
                message=f"Analyzed {len(ticker_metrics)} tickers in {total_time:.2f} seconds",
                processing_time_seconds=total_time,
                missing_tickers=missing_tickers,
                tickers_without_start_data=tickers_without_start_data,
                first_available_dates=first_available_dates
            )
            
        except Exception as e:
            total_time = self._performance_monitor.end_timing("batch_analysis")
            self._logger.error(f"Batch analysis failed: {str(e)}")
            return AnalyzeTickersResponse(
                ticker_metrics=[],
                failed_tickers=[t.symbol for t in request.tickers],
                success=False,
                message=f"Batch analysis failed: {str(e)}",
                processing_time_seconds=total_time,
                missing_tickers=[],
                tickers_without_start_data=[],
                first_available_dates={}
            )
    
    
    def _calculate_metrics(self,
                          ticker: Ticker,
                          prices: pd.Series,
                          dividends: pd.Series,
                          risk_free_rate: float,
                          date_range: DateRange,
                          benchmark_data: pd.Series = None) -> TickerMetrics:
        """Calculate ticker performance metrics."""
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        # Calculate basic metrics using shared calculator
        start_price, end_price, total_return, annualized_return = MetricsCalculator.calculate_basic_metrics(prices)
        
        # Calculate risk metrics using shared calculator
        volatility, sharpe_ratio, max_drawdown, sortino_ratio = MetricsCalculator.calculate_risk_metrics(returns, risk_free_rate)
        var_95 = MetricsCalculator.calculate_var_95(returns)
        
        # Calculate momentum
        momentum_12_1 = self._calculate_momentum(prices)
        
        # Calculate dividend metrics
        dividend_yield, dividend_amount, dividend_frequency, annualized_dividend = self._calculate_dividend_metrics(
            dividends, prices, date_range, start_price.currency
        )
        
        # Calculate beta
        beta = self._calculate_beta_safe(ticker, returns, benchmark_data)
        
        return TickerMetrics(
            ticker=ticker,
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            sortino_ratio=sortino_ratio,
            beta=beta,
            var_95=var_95,
            momentum_12_1=momentum_12_1,
            dividend_yield=dividend_yield,
            dividend_amount=dividend_amount,
            dividend_frequency=dividend_frequency,
            annualized_dividend=annualized_dividend,
            start_price=start_price,
            end_price=end_price
        )
    
    def _calculate_momentum(self, prices: pd.Series) -> Percentage:
        """Calculate 12-1 momentum (skip last month) or available momentum if insufficient data."""
        if len(prices) >= 252:
            # Standard 12-1 momentum: 1 year ago to 1 month ago
            price_252d = prices.iloc[-252]
            price_21d = prices.iloc[-21]
            return Percentage((price_21d - price_252d) / price_252d * 100)
        elif len(prices) >= 21:
            # If we have at least 1 month of data, calculate momentum from start to 1 month ago
            price_start = prices.iloc[0]
            price_21d = prices.iloc[-21]
            return Percentage((price_21d - price_start) / price_start * 100)
        else:
            # Insufficient data for momentum calculation
            return Percentage(0)
    
    def _calculate_dividend_metrics(self, dividends: pd.Series, prices: pd.Series, 
                                  date_range: DateRange, currency: str) -> tuple[Percentage, Money, str, Money]:
        """Calculate dividend-related metrics."""
        dividend_yield = Percentage(0)
        dividend_amount = Money(0, currency)
        dividend_frequency = "Unknown"
        annualized_dividend = Money(0, currency)
        
        if not dividends.empty and not prices.empty:
            # Calculate total dividends received in the period
            total_dividends = dividends.sum()
            dividend_amount = Money(total_dividends, currency)
            
            # Detect dividend payment frequency
            dividend_frequency = self._detect_dividend_frequency(dividends, date_range)
            
            # Calculate annualized dividend based on frequency
            annualized_dividend = self._calculate_annualized_dividend(
                dividends, dividend_frequency, date_range, currency
            )
            
            # Calculate annualized dividend yield using average price
            if annualized_dividend.amount > 0:
                # Use average price over the period for yield calculation
                average_price = prices.mean()
                if average_price > 0:
                    annualized_yield = (float(annualized_dividend.amount) / float(average_price)) * 100
                    dividend_yield = Percentage(annualized_yield)
        
        return dividend_yield, dividend_amount, dividend_frequency, annualized_dividend
    
    def _calculate_beta_safe(self, ticker: Ticker, returns: pd.Series, benchmark_data: pd.Series) -> float:
        """Calculate beta with safe fallback."""
        if benchmark_data is not None and hasattr(benchmark_data, 'empty') and not benchmark_data.empty:
            benchmark_returns = benchmark_data.pct_change().dropna()
            return MetricsCalculator.calculate_beta(returns, benchmark_returns)
        else:
            self._logger.warning(f"No benchmark data available for Beta calculation for {ticker.symbol}")
            return 1.0
    
    def _detect_dividend_frequency(self, dividends: pd.Series, date_range: DateRange) -> str:
        """Detect dividend payment frequency based on payment patterns."""
        if dividends.empty or len(dividends) < 2:
            return "Unknown"
        
        # Calculate days between payments
        dividend_dates = sorted(dividends.index)
        intervals = []
        
        for i in range(1, len(dividend_dates)):
            days_between = (dividend_dates[i] - dividend_dates[i-1]).days
            intervals.append(days_between)
        
        if not intervals:
            return "Unknown"
        
        # Calculate average interval
        avg_interval = sum(intervals) / len(intervals)
        
        # Determine frequency based on average interval
        if avg_interval <= 35:  # ~monthly
            return "Monthly"
        elif avg_interval <= 95:  # ~quarterly
            return "Quarterly"
        elif avg_interval <= 185:  # ~semi-annually
            return "Semi-Annual"
        elif avg_interval <= 370:  # ~annually
            return "Annual"
        else:
            return "Irregular"
    
    def _calculate_annualized_dividend(self, dividends: pd.Series, frequency: str, 
                                     date_range: DateRange, currency: str) -> Money:
        """Calculate annualized dividend based on detected frequency."""
        if dividends.empty:
            return Money(0, currency)
        
        # Calculate total dividends in the period
        total_dividends = dividends.sum()
        
        # Calculate period length in years
        period_days = (date_range.end - date_range.start).days
        period_years = period_days / 365.25
        
        if period_years <= 0:
            return Money(0, currency)
        
        # Calculate annualized dividend based on frequency
        if frequency == "Monthly":
            # For monthly dividends, multiply by 12
            annualized = total_dividends * (12 / len(dividends)) if not dividends.empty else 0
        elif frequency == "Quarterly":
            # For quarterly dividends, multiply by 4
            annualized = total_dividends * (4 / len(dividends)) if not dividends.empty else 0
        elif frequency == "Semi-Annual":
            # For semi-annual dividends, multiply by 2
            annualized = total_dividends * (2 / len(dividends)) if not dividends.empty else 0
        elif frequency == "Annual":
            # For annual dividends, use as-is
            annualized = total_dividends / period_years if period_years > 0 else 0
        else:
            # For irregular or unknown frequency, annualize based on period
            annualized = total_dividends / period_years if period_years > 0 else 0
        
        return Money(annualized, currency)
