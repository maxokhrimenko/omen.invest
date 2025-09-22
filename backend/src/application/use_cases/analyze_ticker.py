from dataclasses import dataclass
from typing import Optional, List
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
            
            # Step 2: Process all tickers using parallel calculation
            self._performance_monitor.start_timing("calculations")
            
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
                processing_time_seconds=total_time
            )
            
        except Exception as e:
            total_time = self._performance_monitor.end_timing("batch_analysis")
            self._logger.error(f"Batch analysis failed: {str(e)}")
            return AnalyzeTickersResponse(
                ticker_metrics=[],
                failed_tickers=[t.symbol for t in request.tickers],
                success=False,
                message=f"Batch analysis failed: {str(e)}",
                processing_time_seconds=total_time
            )
    
    def _calculate_var_95(self, returns: pd.Series) -> Percentage:
        """Calculate VaR 95% with proper validation and error handling."""
        if len(returns) < 5:
            # Insufficient data for reliable VaR calculation
            return Percentage(0)  # Default to 0 when insufficient data
        
        # Calculate VaR using historical simulation method
        var_95_raw = np.percentile(returns, 5) * 100
        
        # Validate VaR result - it should be negative (representing a loss)
        if var_95_raw > 0:
            # Check if we have any negative returns at all
            negative_returns = returns[returns < 0]
            if not negative_returns.empty:
                # Use the worst negative return as VaR
                var_95_raw = negative_returns.min() * 100
            else:
                # No negative returns - this is very unusual for financial data
                # In this case, we cannot calculate a meaningful VaR, so we set it to 0
                # This indicates that there's no historical loss to base VaR on
                var_95_raw = 0
        
        # Additional validation: VaR should not be more extreme than the worst return
        # Only apply this validation if we have a meaningful VaR (negative)
        if var_95_raw < 0:
            worst_return = returns.min() * 100
            if var_95_raw < worst_return:
                var_95_raw = worst_return
        
        return Percentage(var_95_raw)
    
    def _calculate_beta(self, ticker: Ticker, returns: pd.Series, 
                       benchmark_returns: pd.Series) -> float:
        """Calculate Beta for a ticker against benchmark."""
        if len(returns) < 5 or len(benchmark_returns) < 5:
            self._logger.warning(f"Insufficient data for Beta calculation: {len(returns)} ticker, {len(benchmark_returns)} benchmark observations")
            return 1.0  # Default to market beta
        
        # Align the data by date (in case of missing data points)
        common_dates = returns.index.intersection(benchmark_returns.index)
        if len(common_dates) < 5:
            self._logger.warning(f"Insufficient common dates for Beta calculation: {len(common_dates)}")
            return 1.0
        
        aligned_returns = returns.loc[common_dates]
        aligned_benchmark = benchmark_returns.loc[common_dates]
        
        # Ensure data is 1D for covariance calculation
        if aligned_benchmark.ndim > 1:
            aligned_benchmark = aligned_benchmark.iloc[:, 0] if hasattr(aligned_benchmark, 'iloc') else aligned_benchmark.flatten()
        
        # Calculate covariance and variance
        covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
        benchmark_variance = np.var(aligned_benchmark)
        
        if benchmark_variance == 0:
            self._logger.warning("Benchmark variance is zero - cannot calculate Beta")
            return 1.0
        
        beta = covariance / benchmark_variance
        
        # Validate Beta result
        if np.isnan(beta) or np.isinf(beta):
            self._logger.warning(f"Invalid Beta calculation result: {beta}")
            return 1.0
        
        self._logger.debug(f"Calculated Beta for {ticker.symbol}: {beta:.3f}")
        return beta
    
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
        
        # Basic metrics
        start_price = Money(float(prices.iloc[0]))
        end_price = Money(float(prices.iloc[-1]))
        total_return = Percentage(float((end_price.amount - start_price.amount) / start_price.amount) * 100)
        
        # Annualized return
        days = len(returns)
        if days > 0:
            total_return_ratio = float(end_price.amount / start_price.amount)
            annualized_return = Percentage(
                (total_return_ratio ** (252 / days) - 1) * 100
            )
        else:
            annualized_return = Percentage(0)
        
        # Risk metrics
        volatility = Percentage(returns.std() * np.sqrt(252) * 100)
        
        # Sharpe ratio
        rf_daily = risk_free_rate / 252
        excess_returns = returns - rf_daily
        excess_std = excess_returns.std()
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_std if excess_std > 0 else 0
        
        # Max drawdown
        cumulative_returns = (1 + returns).cumprod()
        max_drawdown = Percentage(
            ((cumulative_returns - cumulative_returns.cummax()) / cumulative_returns.cummax()).min() * 100
        )
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if not downside_returns.empty else 0
        sortino_ratio = (
            np.sqrt(252) * excess_returns.mean() / downside_std 
            if downside_std > 0 else 0
        )
        
        # VaR (95%) - Historical simulation method with validation
        # For VaR 95%, we take the 5th percentile of returns (worst 5% of outcomes)
        # This represents the maximum expected loss with 95% confidence
        var_95 = self._calculate_var_95(returns)
        
        # Momentum 12-1 (skip last month)
        momentum_12_1 = Percentage(0)
        if len(prices) >= 252:
            price_252d = prices.iloc[-252]
            price_21d = prices.iloc[-21]
            momentum_12_1 = Percentage((price_21d - price_252d) / price_252d * 100)
        
        # Dividend yield and amount calculation with proper annualization
        dividend_yield = Percentage(0)
        dividend_amount = Money(0)
        dividend_frequency = "Unknown"
        annualized_dividend = Money(0)
        
        if not dividends.empty and not prices.empty:
            # Calculate total dividends received in the period
            total_dividends = dividends.sum()
            dividend_amount = Money(total_dividends, start_price.currency)
            
            # Detect dividend payment frequency
            dividend_frequency = self._detect_dividend_frequency(dividends, date_range)
            
            # Calculate annualized dividend based on frequency
            annualized_dividend = self._calculate_annualized_dividend(
                dividends, dividend_frequency, date_range, start_price.currency
            )
            
            # Calculate annualized dividend yield using average price
            if annualized_dividend.amount > 0:
                # Use average price over the period for yield calculation
                average_price = prices.mean()
                if average_price > 0:
                    annualized_yield = (float(annualized_dividend.amount) / float(average_price)) * 100
                    dividend_yield = Percentage(annualized_yield)
        
        # Beta calculation against S&P 500
        if benchmark_data is not None and hasattr(benchmark_data, 'empty') and not benchmark_data.empty:
            benchmark_returns = benchmark_data.pct_change().dropna()
            beta = self._calculate_beta(ticker, returns, benchmark_returns)
        else:
            self._logger.warning(f"No benchmark data available for Beta calculation for {ticker.symbol}")
            beta = 1.0  # Default to market beta
        
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
