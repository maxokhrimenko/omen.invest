from dataclasses import dataclass
from typing import List, Optional
from .analyze_ticker import AnalyzeTickerUseCase, AnalyzeTickerRequest, TickerMetrics
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange

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

@dataclass
class CompareTickersResponse:
    comparison: Optional[TickerComparison]
    success: bool
    message: str

class CompareTickersUseCase:
    def __init__(self, analyze_ticker_use_case: AnalyzeTickerUseCase):
        self._analyze_ticker_use_case = analyze_ticker_use_case
    
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
    
    def _create_comparison(self, metrics_list: List[TickerMetrics]) -> TickerComparison:
        """Create comparison analysis from ticker metrics."""
        # Sort by different criteria
        by_return = sorted(metrics_list, key=lambda m: m.annualized_return.value, reverse=True)
        by_sharpe = sorted(metrics_list, key=lambda m: m.sharpe_ratio, reverse=True)
        by_risk = sorted(metrics_list, key=lambda m: m.volatility.value)
        
        return TickerComparison(
            metrics=sorted(metrics_list, key=lambda m: m.ticker.symbol),
            best_performer=by_return[0] if by_return else None,
            worst_performer=by_return[-1] if by_return else None,
            best_sharpe=by_sharpe[0] if by_sharpe else None,
            lowest_risk=by_risk[0] if by_risk else None
        )
