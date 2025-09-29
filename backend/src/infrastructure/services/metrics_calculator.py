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
    
    @staticmethod
    def calculate_advanced_metrics(returns: pd.Series, prices: pd.Series, 
                                 risk_free_rate: float = 0.03) -> dict:
        """Calculate advanced financial metrics for ticker comparison."""
        if len(returns) < 5 or len(prices) < 5:
            return {
                'calmar_ratio': 0.0,
                'sortino_ratio': 0.0,
                'ulcer_index': 0.0,
                'time_under_water': 0.0,
                'cvar_95': 0.0,
                'correlation_to_portfolio': 0.0,
                'risk_contribution_absolute': 0.0,
                'risk_contribution_percent': 0.0
            }
        
        # Calculate wealth index (cumulative returns)
        wealth_index = (1 + returns).cumprod()
        
        # 1. MAX DRAWDOWN (MDD) - already calculated in risk metrics
        cumulative_returns = wealth_index
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        mdd = drawdown.min()
        
        # 2. CALMAR RATIO
        # Calculate CAGR (Compound Annual Growth Rate)
        n_days = len(returns)
        annualization_factor = 252
        cagr = (wealth_index.iloc[-1] ** (annualization_factor / n_days)) - 1
        calmar_ratio = cagr / abs(mdd) if mdd != 0 and not np.isnan(mdd) and not np.isnan(cagr) else 0.0
        
        # 3. SORTINO RATIO (use MAR = 0 unless specified)
        mar = 0  # Minimum Acceptable Return
        mar_annual = mar
        downside_returns = returns[returns < mar]
        downside_deviation_squared = (downside_returns ** 2).mean() if len(downside_returns) > 0 else 0
        sortino_ratio = (
            (returns.mean() * annualization_factor - mar_annual) / 
            (np.sqrt(downside_deviation_squared) * np.sqrt(annualization_factor))
            if downside_deviation_squared > 0 and not np.isnan(returns.mean()) else 0.0
        )
        
        # 4. ULCER INDEX (UI)
        # Calculate using prices (not cumulative returns) as per standard formula
        # UI = sqrt(mean(squared_drawdowns))
        # where drawdown = (max_price - current_price) / max_price * 100
        running_max_price = prices.cummax()
        drawdowns = ((running_max_price - prices) / running_max_price * 100).clip(lower=0)
        squared_drawdowns = drawdowns ** 2
        ui = np.sqrt(squared_drawdowns.mean())
        ui = 0.0 if np.isnan(ui) else ui
        
        # 5. TIME UNDER WATER (TUW)
        # Calculate using actual prices (not cumulative returns) for more meaningful results
        # TUW = fraction of time spent below running maximum price
        running_max_price = prices.cummax()
        below_peak_price = prices < running_max_price
        tuw = below_peak_price.mean()
        tuw = 0.0 if np.isnan(tuw) else tuw
        
        # 6. HISTORICAL EXPECTED SHORTFALL (CVaR_95)
        sorted_returns = returns.sort_values()
        k = int(0.05 * len(sorted_returns))
        k = max(1, k)  # Ensure at least 1 observation
        cvar_95 = sorted_returns.iloc[:k].mean()
        cvar_95 = 0.0 if np.isnan(cvar_95) else cvar_95
        
        # 7. CORRELATION TO PORTFOLIO (placeholder - will be calculated in comparison context)
        correlation_to_portfolio = 0.0
        
        # 8. RISK CONTRIBUTION (placeholder - will be calculated in portfolio context)
        risk_contribution_absolute = 0.0
        risk_contribution_percent = 0.0
        
        return {
            'calmar_ratio': float(calmar_ratio) if not np.isnan(calmar_ratio) else 0.0,
            'sortino_ratio': float(sortino_ratio) if not np.isnan(sortino_ratio) else 0.0,
            'ulcer_index': float(ui) if not np.isnan(ui) else 0.0,
            'time_under_water': float(tuw) if not np.isnan(tuw) else 0.0,
            'cvar_95': float(cvar_95) if not np.isnan(cvar_95) else 0.0,
            'correlation_to_portfolio': float(correlation_to_portfolio) if not np.isnan(correlation_to_portfolio) else 0.0,
            'risk_contribution_absolute': float(risk_contribution_absolute) if not np.isnan(risk_contribution_absolute) else 0.0,
            'risk_contribution_percent': float(risk_contribution_percent) if not np.isnan(risk_contribution_percent) else 0.0
        }
    
    @staticmethod
    def calculate_portfolio_correlation_and_risk_contribution(
        ticker_returns: pd.Series, 
        portfolio_returns: pd.Series,
        portfolio_weights: dict,
        ticker_symbol: str
    ) -> tuple[float, float, float]:
        """Calculate correlation to portfolio and risk contribution metrics."""
        if len(ticker_returns) < 5 or len(portfolio_returns) < 5:
            return 0.0, 0.0, 0.0
        
        # Align data by date
        common_dates = ticker_returns.index.intersection(portfolio_returns.index)
        if len(common_dates) < 5:
            return 0.0, 0.0, 0.0
        
        aligned_ticker = ticker_returns.loc[common_dates]
        aligned_portfolio = portfolio_returns.loc[common_dates]
        
        # 7. CORRELATION TO PORTFOLIO
        correlation = np.corrcoef(aligned_ticker, aligned_portfolio)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
        
        # 8. RISK CONTRIBUTION TO PORTFOLIO VARIANCE
        # Get ticker weight
        ticker_weight = portfolio_weights.get(ticker_symbol, 0.0)
        
        # Calculate individual ticker variance and portfolio variance
        ticker_var = np.var(aligned_ticker)
        portfolio_var = np.var(aligned_portfolio)
        
        # For risk contribution, we need to understand how much this ticker contributes to portfolio risk
        # Since we don't have the full covariance matrix, we use a more realistic approximation:
        # The ticker's risk contribution is proportional to its weight and its relative volatility
        
        # Calculate the ticker's relative volatility contribution
        # This is a more intuitive measure: how much does this ticker's volatility contribute to portfolio risk?
        if portfolio_var > 0:
            # Method 1: Weighted variance contribution
            # This gives a more realistic sense of risk contribution
            risk_contribution_absolute = ticker_weight * ticker_var
            
            # Method 2: Relative volatility contribution (more intuitive)
            # How much of the portfolio's total variance comes from this ticker's volatility?
            # We need to calculate the total weighted variance across all tickers
            # Since we don't have all ticker variances here, we use a simplified approach
            # The risk contribution percentage should be proportional to the ticker's weight and volatility
            # relative to the average volatility in the portfolio
            
            # Simplified calculation: assume average volatility across portfolio
            # This gives a more realistic range of values
            avg_volatility = np.sqrt(portfolio_var)  # Portfolio volatility as proxy for average
            ticker_volatility = np.sqrt(ticker_var)
            
            # Risk contribution as percentage of portfolio risk
            # Higher volatility tickers contribute more to portfolio risk
            if avg_volatility > 0:
                volatility_ratio = ticker_volatility / avg_volatility
                risk_contribution_percent = ticker_weight * volatility_ratio * 100
            else:
                risk_contribution_percent = ticker_weight * 100
        else:
            risk_contribution_absolute = 0.0
            risk_contribution_percent = 0.0
        
        # Ensure values are not NaN and are reasonable
        risk_contribution_absolute = 0.0 if np.isnan(risk_contribution_absolute) else max(0.0, risk_contribution_absolute)
        risk_contribution_percent = 0.0 if np.isnan(risk_contribution_percent) else max(0.0, min(100.0, risk_contribution_percent))
        
        return float(correlation), float(risk_contribution_absolute), float(risk_contribution_percent)