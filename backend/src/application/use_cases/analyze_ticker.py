from dataclasses import dataclass
from typing import Optional, List
import pandas as pd
import numpy as np
from ..interfaces.repositories import MarketDataRepository
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money
from ...domain.value_objects.percentage import Percentage

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

class AnalyzeTickerUseCase:
    def __init__(self, market_data_repo: MarketDataRepository):
        self._market_data_repo = market_data_repo
    
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
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                request.ticker,
                prices,
                dividend_history,
                request.risk_free_rate,
                request.date_range
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
    
    def _calculate_metrics(self,
                          ticker: Ticker,
                          prices: pd.Series,
                          dividends: pd.Series,
                          risk_free_rate: float,
                          date_range: DateRange) -> TickerMetrics:
        """Calculate ticker performance metrics."""
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        # Basic metrics
        start_price = Money(prices.iloc[0])
        end_price = Money(prices.iloc[-1])
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
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0
        
        # Max drawdown
        cumulative_returns = (1 + returns).cumprod()
        max_drawdown = Percentage(
            ((cumulative_returns - cumulative_returns.cummax()) / cumulative_returns.cummax()).min() * 100
        )
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        sortino_ratio = (
            np.sqrt(252) * excess_returns.mean() / downside_returns.std() 
            if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
        )
        
        # VaR (95%)
        var_95 = Percentage(np.percentile(returns, 5) * 100)
        
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
        
        # Beta (placeholder - would need benchmark data)
        beta = 1.0
        
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
            annualized = total_dividends * (12 / len(dividends)) if len(dividends) > 0 else 0
        elif frequency == "Quarterly":
            # For quarterly dividends, multiply by 4
            annualized = total_dividends * (4 / len(dividends)) if len(dividends) > 0 else 0
        elif frequency == "Semi-Annual":
            # For semi-annual dividends, multiply by 2
            annualized = total_dividends * (2 / len(dividends)) if len(dividends) > 0 else 0
        elif frequency == "Annual":
            # For annual dividends, use as-is
            annualized = total_dividends / period_years if period_years > 0 else 0
        else:
            # For irregular or unknown frequency, annualize based on period
            annualized = total_dividends / period_years if period_years > 0 else 0
        
        return Money(annualized, currency)
