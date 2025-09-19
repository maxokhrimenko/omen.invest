from dataclasses import dataclass
from typing import Optional, Dict
import pandas as pd
import numpy as np
from ..interfaces.repositories import MarketDataRepository
from ...domain.entities.portfolio import Portfolio
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money
from ...domain.value_objects.percentage import Percentage

@dataclass
class AnalyzePortfolioRequest:
    portfolio: Portfolio
    date_range: DateRange
    risk_free_rate: float = 0.03

@dataclass
class PortfolioMetrics:
    total_return: Percentage
    annualized_return: Percentage
    volatility: Percentage
    sharpe_ratio: float
    max_drawdown: Percentage
    sortino_ratio: float
    calmar_ratio: float
    var_95: Percentage
    beta: float
    start_value: Money
    end_value: Money

@dataclass
class AnalyzePortfolioResponse:
    metrics: Optional[PortfolioMetrics]
    success: bool
    message: str

class AnalyzePortfolioUseCase:
    def __init__(self, market_data_repo: MarketDataRepository):
        self._market_data_repo = market_data_repo
    
    def execute(self, request: AnalyzePortfolioRequest) -> AnalyzePortfolioResponse:
        try:
            # Get price history for all tickers
            price_history = self._market_data_repo.get_price_history(
                request.portfolio.get_tickers(),
                request.date_range
            )
            
            if not price_history:
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message="No price data available for portfolio analysis"
                )
            
            # Calculate portfolio value over time
            portfolio_values = self._calculate_portfolio_values(
                request.portfolio, price_history
            )
            
            if portfolio_values.empty:
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message="Unable to calculate portfolio values"
                )
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                portfolio_values, 
                request.risk_free_rate
            )
            
            return AnalyzePortfolioResponse(
                metrics=metrics,
                success=True,
                message="Portfolio analysis completed successfully"
            )
            
        except Exception as e:
            return AnalyzePortfolioResponse(
                metrics=None,
                success=False,
                message=f"Portfolio analysis failed: {str(e)}"
            )
    
    def _calculate_portfolio_values(self, 
                                   portfolio: Portfolio, 
                                   price_history: Dict[Ticker, pd.Series]) -> pd.Series:
        """Calculate portfolio value over time."""
        # Align all price series by date
        price_df = pd.DataFrame(price_history)
        if price_df.empty:
            return pd.Series(dtype=float)
        
        # Calculate position values
        portfolio_values = pd.Series(0.0, index=price_df.index)
        
        for position in portfolio:
            if position.ticker in price_history:
                ticker_prices = price_history[position.ticker]
                position_values = ticker_prices * float(position.quantity)
                portfolio_values = portfolio_values.add(position_values, fill_value=0)
        
        return portfolio_values.dropna()
    
    def _calculate_metrics(self, 
                          portfolio_values: pd.Series, 
                          risk_free_rate: float) -> PortfolioMetrics:
        """Calculate portfolio performance metrics."""
        # Calculate returns
        returns = portfolio_values.pct_change().dropna()
        
        # Basic metrics
        start_value = Money(portfolio_values.iloc[0])
        end_value = Money(portfolio_values.iloc[-1])
        total_return = Percentage(float((end_value.amount - start_value.amount) / start_value.amount) * 100)
        
        # Annualized return
        days = len(returns)
        if days > 0:
            total_return_ratio = float(end_value.amount / start_value.amount)
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
        
        # Calmar ratio
        calmar_ratio = (
            float(annualized_return.value) / abs(float(max_drawdown.value)) 
            if float(max_drawdown.value) != 0 else 0
        )
        
        # VaR (95%)
        var_95 = Percentage(np.percentile(returns, 5) * 100)
        
        # Beta (placeholder - would need benchmark data)
        beta = 1.0
        
        return PortfolioMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            var_95=var_95,
            beta=beta,
            start_value=start_value,
            end_value=end_value
        )
