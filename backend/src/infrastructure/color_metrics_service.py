"""
Implementation of metrics color coding service based on METRICS_MEMORANDUM.md thresholds.
"""

from typing import Union, Dict, Tuple
from ..application.interfaces.metrics_color_service import MetricsColorService, ColorCode, MetricLevel


class ColorMetricsService(MetricsColorService):
    """Service for color-coding financial metrics based on performance thresholds."""
    
    def __init__(self):
        """Initialize the color service with thresholds from METRICS_MEMORANDUM.md."""
        self._portfolio_thresholds = self._initialize_portfolio_thresholds()
        self._ticker_thresholds = self._initialize_ticker_thresholds()
    
    def _initialize_portfolio_thresholds(self) -> Dict[str, Tuple[float, float]]:
        """Initialize portfolio metric thresholds (bad, normal, excellent)."""
        return {
            # Return Metrics
            "total_return": (10.0, 30.0),  # Bad: <10%, Normal: 10-30%, Excellent: >30%
            "annualized_return": (5.0, 15.0),  # Bad: <5%, Normal: 5-15%, Excellent: >15%
            
            # Risk-Adjusted Return Metrics
            "sharpe_ratio": (0.5, 1.5),  # Bad: <0.5, Normal: 0.5-1.5, Excellent: >1.5
            "sortino_ratio": (1.0, 2.0),  # Bad: <1.0, Normal: 1.0-2.0, Excellent: >2.0
            "calmar_ratio": (0.5, 1.0),  # Bad: <0.5, Normal: 0.5-1.0, Excellent: >1.0
            
            # Risk Metrics
            "max_drawdown": (-30.0, -15.0),  # Bad: >-30%, Normal: -30% to -15%, Excellent: >-15%
            "volatility": (20.0, 10.0),  # Bad: >20%, Normal: 10-20%, Excellent: <10%
            "var_95": (-2.0, -1.0),  # Bad: >-2%, Normal: -2% to -1%, Excellent: >-1%
            "beta": (1.3, 0.7),  # Bad: >1.3, Normal: 0.7-1.3, Excellent: <0.7
        }
    
    def _initialize_ticker_thresholds(self) -> Dict[str, Tuple[float, float]]:
        """Initialize ticker metric thresholds (bad, normal, excellent)."""
        return {
            # Return Metrics
            "annualized_return": (5.0, 20.0),  # Bad: <5%, Normal: 5-20%, Excellent: >20%
            
            # Risk-Adjusted Return Metrics
            "sharpe_ratio": (0.5, 1.5),  # Same as portfolio
            "sortino_ratio": (0.8, 2.0),  # Bad: <0.8, Normal: 0.8-2.0, Excellent: >2.0
            
            # Risk Metrics
            "max_drawdown": (-50.0, -30.0),  # Bad: >-50%, Normal: -50% to -30%, Excellent: >-30%
            "volatility": (50.0, 30.0),  # Bad: >50%, Normal: 30-50%, Excellent: <30%
            "beta": (1.5, 0.5),  # Bad: >1.5, Normal: 0.5-1.5, Excellent: <0.5
            "var_95": (-4.0, -2.0),  # Bad: >-4%, Normal: -4% to -2%, Excellent: >-2%
            
            # Momentum and Yield Metrics
            "momentum_12_1": (0.0, 20.0),  # Bad: <0%, Normal: 0-20%, Excellent: >20%
            "dividend_yield": (1.0, 4.0),  # Bad: <1%, Normal: 1-4%, Excellent: >4%
            "current_yield": (1.0, 4.0),  # Same as dividend_yield
            "average_yield": (1.0, 4.0),  # Same as dividend_yield
            "maximum_yield": (2.0, 6.0),  # Bad: <2%, Normal: 2-6%, Excellent: >6%
        }
    
    def get_color_for_metric(self, metric_name: str, value: Union[float, int], context: str = "portfolio") -> ColorCode:
        """Get color code for a specific metric value."""
        level = self.get_level_for_metric(metric_name, value, context)
        
        if level == MetricLevel.BAD:
            return ColorCode.RED
        elif level == MetricLevel.NORMAL:
            return ColorCode.YELLOW
        else:  # EXCELLENT
            return ColorCode.GREEN
    
    def get_level_for_metric(self, metric_name: str, value: Union[float, int], context: str = "portfolio") -> MetricLevel:
        """Get performance level for a specific metric value."""
        thresholds = self._portfolio_thresholds if context == "portfolio" else self._ticker_thresholds
        
        if metric_name not in thresholds:
            return MetricLevel.NORMAL  # Default to normal if metric not found
        
        bad_threshold, excellent_threshold = thresholds[metric_name]
        
        # Handle cases for metrics where lower is better
        if metric_name in ["volatility", "beta"]:
            # For other metrics where lower is better
            if value > bad_threshold:
                return MetricLevel.BAD
            elif value > excellent_threshold:
                return MetricLevel.NORMAL
            else:
                return MetricLevel.EXCELLENT
        elif metric_name in ["max_drawdown", "var_95"]:
            # For max_drawdown and var_95, less negative is better (closer to 0 is better)
            if metric_name == "max_drawdown":
                if value < bad_threshold:  # More negative than -30%
                    return MetricLevel.BAD
                elif value < excellent_threshold:  # Between -30% and -15%
                    return MetricLevel.NORMAL
                else:  # Less negative than -15% (closer to 0)
                    return MetricLevel.EXCELLENT
            elif metric_name == "var_95":
                if value < bad_threshold:  # More negative than -2%
                    return MetricLevel.BAD
                elif value < excellent_threshold:  # Between -2% and -1%
                    return MetricLevel.NORMAL
                else:  # Less negative than -1% (closer to 0)
                    return MetricLevel.EXCELLENT
        else:
            # For metrics where higher is better
            if value < bad_threshold:
                return MetricLevel.BAD
            elif value < excellent_threshold:
                return MetricLevel.NORMAL
            else:
                return MetricLevel.EXCELLENT
    
    def colorize_text(self, text: str, color: ColorCode) -> str:
        """Apply color to text."""
        return f"{color.value}{text}{ColorCode.RESET.value}"
    
    def colorize_percentage(self, percentage: float, metric_name: str, context: str = "portfolio") -> str:
        """Colorize a percentage value based on metric thresholds."""
        color = self.get_color_for_metric(metric_name, percentage, context)
        formatted_value = f"{percentage:.1f}%"
        return self.colorize_text(formatted_value, color)
    
    def colorize_ratio(self, ratio: float, metric_name: str, context: str = "portfolio") -> str:
        """Colorize a ratio value based on metric thresholds."""
        color = self.get_color_for_metric(metric_name, ratio, context)
        formatted_value = f"{ratio:.2f}"
        return self.colorize_text(formatted_value, color)
    
    def colorize_money(self, amount: float, metric_name: str = "money", context: str = "portfolio") -> str:
        """Colorize a money value (typically no color coding for money amounts)."""
        return f"${amount:.2f}"
    
    def colorize_ticker_symbol(self, symbol: str) -> str:
        """Colorize ticker symbol (typically blue for visibility)."""
        return self.colorize_text(symbol, ColorCode.BLUE)
    
    def get_metric_summary_color(self, metrics: Dict[str, float], context: str = "portfolio") -> ColorCode:
        """
        Get overall color for a set of metrics based on weighted performance.
        This can be used for overall portfolio or ticker assessment.
        """
        if not metrics:
            return ColorCode.WHITE
        
        # Weight different metrics based on importance
        weights = {
            "annualized_return": 0.3,
            "sharpe_ratio": 0.25,
            "max_drawdown": 0.2,
            "volatility": 0.15,
            "sortino_ratio": 0.1
        }
        
        weighted_score = 0
        total_weight = 0
        
        for metric_name, weight in weights.items():
            if metric_name in metrics:
                level = self.get_level_for_metric(metric_name, metrics[metric_name], context)
                score = 1 if level == MetricLevel.EXCELLENT else 0.5 if level == MetricLevel.NORMAL else 0
                weighted_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return ColorCode.WHITE
        
        average_score = weighted_score / total_weight
        
        if average_score >= 0.8:
            return ColorCode.GREEN
        elif average_score >= 0.5:
            return ColorCode.YELLOW
        else:
            return ColorCode.RED
