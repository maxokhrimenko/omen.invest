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
                request.risk_free_rate
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
                          risk_free_rate: float) -> TickerMetrics:
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
        
        # Dividend yield
        dividend_yield = Percentage(0)
        if not dividends.empty and start_price.amount > 0:
            annual_dividends = dividends.sum()
            dividend_yield = Percentage(annual_dividends / float(start_price.amount) * 100)
        
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
            start_price=start_price,
            end_price=end_price
        )
