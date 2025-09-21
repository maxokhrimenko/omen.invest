"""
Interface for metrics color coding service.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Union
from ..use_cases.analyze_portfolio import PortfolioMetrics
from ..use_cases.analyze_ticker import TickerMetrics


class ColorCode(Enum):
    """Color codes for terminal output."""
    RED = "\033[91m"      # Bad
    YELLOW = "\033[93m"   # Normal/Warning
    GREEN = "\033[92m"    # Excellent
    BLUE = "\033[94m"     # Info
    MAGENTA = "\033[95m"  # Special
    CYAN = "\033[96m"     # Highlight
    WHITE = "\033[97m"    # Default
    RESET = "\033[0m"     # Reset to default


class MetricLevel(Enum):
    """Metric performance levels."""
    BAD = "bad"
    NORMAL = "normal"
    EXCELLENT = "excellent"


class MetricsColorService(ABC):
    """Interface for color-coding financial metrics based on performance thresholds."""
    
    @abstractmethod
    def get_color_for_metric(self, metric_name: str, value: Union[float, int], context: str = "portfolio") -> ColorCode:
        """
        Get color code for a specific metric value.
        
        Args:
            metric_name: Name of the metric (e.g., 'annualized_return', 'sharpe_ratio')
            value: The metric value
            context: Context for the metric ('portfolio' or 'ticker')
            
        Returns:
            ColorCode enum value
        """
        pass
    
    @abstractmethod
    def get_level_for_metric(self, metric_name: str, value: Union[float, int], context: str = "portfolio") -> MetricLevel:
        """
        Get performance level for a specific metric value.
        
        Args:
            metric_name: Name of the metric
            value: The metric value
            context: Context for the metric ('portfolio' or 'ticker')
            
        Returns:
            MetricLevel enum value
        """
        pass
    
    @abstractmethod
    def colorize_text(self, text: str, color: ColorCode) -> str:
        """
        Apply color to text.
        
        Args:
            text: Text to colorize
            color: Color to apply
            
        Returns:
            Colorized text string
        """
        pass
    
    @abstractmethod
    def colorize_percentage(self, percentage: float, metric_name: str, context: str = "portfolio") -> str:
        """
        Colorize a percentage value based on metric thresholds.
        
        Args:
            percentage: Percentage value
            metric_name: Name of the metric
            context: Context for the metric
            
        Returns:
            Colorized percentage string
        """
        pass
    
    @abstractmethod
    def colorize_ratio(self, ratio: float, metric_name: str, context: str = "portfolio") -> str:
        """
        Colorize a ratio value based on metric thresholds.
        
        Args:
            ratio: Ratio value
            metric_name: Name of the metric
            context: Context for the metric
            
        Returns:
            Colorized ratio string
        """
        pass
