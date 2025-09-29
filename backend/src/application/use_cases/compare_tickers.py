from dataclasses import dataclass
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
from .analyze_ticker import AnalyzeTickerUseCase, AnalyzeTickerRequest, TickerMetrics
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...infrastructure.services.metrics_calculator import MetricsCalculator

@dataclass
class CompareTickersRequest:
    tickers: List[Ticker]
    date_range: DateRange
    risk_free_rate: float = 0.03

@dataclass
class TickerComparison:
    metrics: List[TickerMetrics]
    best_performer: Optional[TickerMetrics]
    worst_performer: Optional[TickerMetrics]
    best_sharpe: Optional[TickerMetrics]
    lowest_risk: Optional[TickerMetrics]
    # Advanced metrics rankings
    best_calmar: Optional[TickerMetrics]
    worst_calmar: Optional[TickerMetrics]
    best_sortino: Optional[TickerMetrics]
    worst_sortino: Optional[TickerMetrics]
    best_max_drawdown: Optional[TickerMetrics]
    worst_max_drawdown: Optional[TickerMetrics]
    best_ulcer: Optional[TickerMetrics]
    worst_ulcer: Optional[TickerMetrics]
    best_time_under_water: Optional[TickerMetrics]
    worst_time_under_water: Optional[TickerMetrics]
    best_cvar: Optional[TickerMetrics]
    worst_cvar: Optional[TickerMetrics]
    best_correlation: Optional[TickerMetrics]
    worst_correlation: Optional[TickerMetrics]
    best_risk_contribution: Optional[TickerMetrics]
    worst_risk_contribution: Optional[TickerMetrics]

@dataclass
class CompareTickersResponse:
    comparison: Optional[TickerComparison]
    success: bool
    message: str

class CompareTickersUseCase:
    def __init__(self, analyze_ticker_use_case: AnalyzeTickerUseCase, market_data_repo=None):
        self._analyze_ticker_use_case = analyze_ticker_use_case
        self._market_data_repo = market_data_repo
    
    def execute(self, request: CompareTickersRequest) -> CompareTickersResponse:
        try:
            if not request.tickers:
                return CompareTickersResponse(
                    comparison=None,
                    success=False,
                    message="No tickers provided for comparison"
                )
            
            # Analyze each ticker
            ticker_metrics = []
            failed_tickers = []
            
            for ticker in request.tickers:
                analyze_request = AnalyzeTickerRequest(
                    ticker=ticker,
                    date_range=request.date_range,
                    risk_free_rate=request.risk_free_rate
                )
                
                response = self._analyze_ticker_use_case.execute(analyze_request)
                if response.success and response.metrics:
                    ticker_metrics.append(response.metrics)
                else:
                    failed_tickers.append(ticker.symbol)
            
            if not ticker_metrics:
                return CompareTickersResponse(
                    comparison=None,
                    success=False,
                    message="No ticker analysis succeeded"
                )
            
            # Calculate portfolio-level metrics and update correlation/risk contribution
            if self._market_data_repo and len(ticker_metrics) > 1:
                ticker_metrics = self._update_portfolio_metrics(ticker_metrics, request)
            
            # Find best/worst performers
            comparison = self._create_comparison(ticker_metrics)
            
            message = f"Compared {len(ticker_metrics)} tickers successfully"
            if failed_tickers:
                message += f" (failed: {', '.join(failed_tickers)})"
            
            return CompareTickersResponse(
                comparison=comparison,
                success=True,
                message=message
            )
            
        except Exception as e:
            return CompareTickersResponse(
                comparison=None,
                success=False,
                message=f"Ticker comparison failed: {str(e)}"
            )
    
    def _update_portfolio_metrics(self, ticker_metrics: List[TickerMetrics], request: CompareTickersRequest) -> List[TickerMetrics]:
        """Update ticker metrics with portfolio-level correlation and risk contribution."""
        try:
            # Get price data for all tickers
            price_data = {}
            for metrics in ticker_metrics:
                prices = self._market_data_repo.get_price_history([metrics.ticker], request.date_range)
                if metrics.ticker in prices and not prices[metrics.ticker].empty:
                    price_data[metrics.ticker.symbol] = prices[metrics.ticker]
            
            if len(price_data) < 2:
                return ticker_metrics
            
            # Calculate portfolio returns (equal weight for now)
            portfolio_returns = self._calculate_portfolio_returns(price_data)
            
            # Calculate portfolio weights (equal weight for now)
            portfolio_weights = {symbol: 1.0 / len(price_data) for symbol in price_data.keys()}
            
            # Update each ticker's correlation and risk contribution
            updated_metrics = []
            for metrics in ticker_metrics:
                if metrics.ticker.symbol in price_data:
                    ticker_prices = price_data[metrics.ticker.symbol]
                    ticker_returns = ticker_prices.pct_change().dropna()
                    
                    correlation, risk_abs, risk_pct = MetricsCalculator.calculate_portfolio_correlation_and_risk_contribution(
                        ticker_returns, portfolio_returns, portfolio_weights, metrics.ticker.symbol
                    )
                    
                    # Create updated metrics with new correlation and risk contribution
                    updated_metrics.append(TickerMetrics(
                        ticker=metrics.ticker,
                        total_return=metrics.total_return,
                        annualized_return=metrics.annualized_return,
                        volatility=metrics.volatility,
                        sharpe_ratio=metrics.sharpe_ratio,
                        max_drawdown=metrics.max_drawdown,
                        sortino_ratio=metrics.sortino_ratio,
                        beta=metrics.beta,
                        var_95=metrics.var_95,
                        momentum_12_1=metrics.momentum_12_1,
                        dividend_yield=metrics.dividend_yield,
                        dividend_amount=metrics.dividend_amount,
                        dividend_frequency=metrics.dividend_frequency,
                        annualized_dividend=metrics.annualized_dividend,
                        start_price=metrics.start_price,
                        end_price=metrics.end_price,
                        calmar_ratio=metrics.calmar_ratio,
                        ulcer_index=metrics.ulcer_index,
                        time_under_water=metrics.time_under_water,
                        cvar_95=metrics.cvar_95,
                        correlation_to_portfolio=correlation,
                        risk_contribution_absolute=risk_abs,
                        risk_contribution_percent=risk_pct
                    ))
                else:
                    updated_metrics.append(metrics)
            
            return updated_metrics
            
        except Exception as e:
            # If portfolio calculation fails, return original metrics
            return ticker_metrics
    
    def _calculate_portfolio_returns(self, price_data: Dict[str, pd.Series]) -> pd.Series:
        """Calculate equal-weight portfolio returns."""
        if not price_data:
            return pd.Series(dtype=float)
        
        # Align all price series by date
        common_dates = None
        for prices in price_data.values():
            if common_dates is None:
                common_dates = prices.index
            else:
                common_dates = common_dates.intersection(prices.index)
        
        if common_dates is None or len(common_dates) == 0:
            return pd.Series(dtype=float)
        
        # Calculate equal-weight portfolio values
        portfolio_values = pd.Series(0.0, index=common_dates)
        weight = 1.0 / len(price_data)
        
        for symbol, prices in price_data.items():
            aligned_prices = prices.loc[common_dates]
            portfolio_values += weight * aligned_prices
        
        # Calculate portfolio returns
        return portfolio_values.pct_change().dropna()
    
    def _create_comparison(self, metrics_list: List[TickerMetrics]) -> TickerComparison:
        """Create comparison analysis from ticker metrics."""
        # Sort by different criteria
        by_return = sorted(metrics_list, key=lambda m: m.annualized_return.value, reverse=True)
        by_sharpe = sorted(metrics_list, key=lambda m: m.sharpe_ratio, reverse=True)
        by_risk = sorted(metrics_list, key=lambda m: m.volatility.value)
        
        # Advanced metrics sorting
        by_calmar = sorted(metrics_list, key=lambda m: m.calmar_ratio, reverse=True)  # Higher is better
        by_sortino = sorted(metrics_list, key=lambda m: m.sortino_ratio, reverse=True)  # Higher is better
        by_max_drawdown = sorted(metrics_list, key=lambda m: m.max_drawdown.value, reverse=True)  # Less negative is better (closer to 0)
        by_ulcer = sorted(metrics_list, key=lambda m: m.ulcer_index)  # Lower is better
        by_time_under_water = sorted(metrics_list, key=lambda m: m.time_under_water)  # Lower is better
        by_cvar = sorted(metrics_list, key=lambda m: m.cvar_95)  # Lower is better (more negative)
        by_correlation = sorted(metrics_list, key=lambda m: abs(m.correlation_to_portfolio))  # Lower absolute correlation is better for diversification
        by_risk_contribution = sorted(metrics_list, key=lambda m: m.risk_contribution_percent)  # Lower risk contribution is better
        
        return TickerComparison(
            metrics=sorted(metrics_list, key=lambda m: m.ticker.symbol),
            best_performer=by_return[0] if by_return else None,
            worst_performer=by_return[-1] if by_return else None,
            best_sharpe=by_sharpe[0] if by_sharpe else None,
            lowest_risk=by_risk[0] if by_risk else None,
            # Advanced metrics rankings
            best_calmar=by_calmar[0] if by_calmar else None,
            worst_calmar=by_calmar[-1] if by_calmar else None,
            best_sortino=by_sortino[0] if by_sortino else None,
            worst_sortino=by_sortino[-1] if by_sortino else None,
            best_max_drawdown=by_max_drawdown[0] if by_max_drawdown else None,
            worst_max_drawdown=by_max_drawdown[-1] if by_max_drawdown else None,
            best_ulcer=by_ulcer[0] if by_ulcer else None,
            worst_ulcer=by_ulcer[-1] if by_ulcer else None,
            best_time_under_water=by_time_under_water[0] if by_time_under_water else None,
            worst_time_under_water=by_time_under_water[-1] if by_time_under_water else None,
            best_cvar=by_cvar[0] if by_cvar else None,
            worst_cvar=by_cvar[-1] if by_cvar else None,
            best_correlation=by_correlation[0] if by_correlation else None,
            worst_correlation=by_correlation[-1] if by_correlation else None,
            best_risk_contribution=by_risk_contribution[0] if by_risk_contribution else None,
            worst_risk_contribution=by_risk_contribution[-1] if by_risk_contribution else None
        )
