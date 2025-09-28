"""
Shared metrics calculation service for portfolio and ticker analysis.
"""

import pandas as pd
import numpy as np
from typing import Tuple
from ...domain.value_objects.money import Money
from ...domain.value_objects.percentage import Percentage


class MetricsCalculator:
    """Service for calculating financial metrics."""
    
    @staticmethod
    def calculate_basic_metrics(prices: pd.Series) -> Tuple[Money, Money, Percentage, Percentage]:
        """Calculate basic price and return metrics."""
        start_price = Money(float(prices.iloc[0]))
        end_price = Money(float(prices.iloc[-1]))
        
        if start_price.amount == 0:
            raise ValueError("Start price is zero - cannot calculate returns")
        
        total_return = Percentage(float((end_price.amount - start_price.amount) / start_price.amount) * 100)
        
        # Annualized return
        days = len(prices)
        if days > 0:
            total_return_ratio = float(end_price.amount / start_price.amount)
            annualized_return = Percentage((total_return_ratio ** (252 / days) - 1) * 100)
        else:
            annualized_return = Percentage(0)
        
        return start_price, end_price, total_return, annualized_return
    
    @staticmethod
    def calculate_risk_metrics(returns: pd.Series, risk_free_rate: float) -> Tuple[Percentage, float, Percentage, float]:
        """Calculate risk metrics."""
        # Volatility
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
        
        return volatility, sharpe_ratio, max_drawdown, sortino_ratio
    
    @staticmethod
    def calculate_calmar_ratio(annualized_return: Percentage, max_drawdown: Percentage) -> float:
        """Calculate Calmar ratio."""
        return (
            float(annualized_return.value) / abs(float(max_drawdown.value)) 
            if float(max_drawdown.value) != 0 else 0
        )
    
    @staticmethod
    def calculate_var_95(returns: pd.Series) -> Percentage:
        """Calculate VaR 95% with proper validation and error handling."""
        if len(returns) < 5:
            return Percentage(0)
        
        # Calculate VaR using historical simulation method
        var_95_raw = np.percentile(returns, 5) * 100
        
        # Validate VaR result - it should be negative (representing a loss)
        if var_95_raw > 0:
            negative_returns = returns[returns < 0]
            var_95_raw = negative_returns.min() * 100 if not negative_returns.empty else 0
        
        # Ensure VaR is not more extreme than the worst return
        if var_95_raw < 0:
            worst_return = returns.min() * 100
            var_95_raw = max(var_95_raw, worst_return)
        
        return Percentage(var_95_raw)
    
    @staticmethod
    def calculate_beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate Beta for returns against benchmark."""
        if len(returns) < 5 or len(benchmark_returns) < 5:
            return 1.0
        
        # Align the data by date
        common_dates = returns.index.intersection(benchmark_returns.index)
        if len(common_dates) < 5:
            return 1.0
        
        aligned_returns = returns.loc[common_dates]
        aligned_benchmark = benchmark_returns.loc[common_dates]
        
        # Ensure data is 1D for covariance calculation
        if aligned_benchmark.ndim > 1:
            aligned_benchmark = aligned_benchmark.iloc[:, 0] if hasattr(aligned_benchmark, 'iloc') else aligned_benchmark.flatten()
        
        # Calculate covariance and variance
        covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
        benchmark_variance = np.var(aligned_benchmark)
        
        if benchmark_variance == 0 or np.isnan(covariance) or np.isnan(benchmark_variance):
            return 1.0
        
        beta = covariance / benchmark_variance
        return 1.0 if np.isnan(beta) or np.isinf(beta) else beta
