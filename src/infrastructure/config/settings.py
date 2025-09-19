import yaml
import os
from typing import Dict, Any

class Settings:
    """Configuration settings manager."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self._config_path = config_path
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from YAML file."""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as file:
                    return yaml.safe_load(file) or {}
            else:
                return self._get_default_settings()
        except Exception:
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings if config file is not available."""
        return {
            'defaults': {
                'start_date': '2024-03-01',
                'risk_free_rate': 0.03,
                'portfolio_file': 'input/input.csv'
            },
            'analysis': {
                'min_trading_days': 30,
                'confidence_level': 0.95,
                'annualization_factor': 252
            },
            'display': {
                'decimal_places': 2,
                'percentage_places': 1,
                'currency_symbol': '$'
            },
            'thresholds': {
                'annual_return': {'excellent': 0.15, 'good': 0.10, 'poor': 0.05},
                'sharpe_ratio': {'excellent': 1.5, 'good': 1.0, 'poor': 0.5},
                'max_drawdown': {'excellent': 0.15, 'good': 0.25, 'poor': 0.40},
                'volatility': {'excellent': 0.15, 'good': 0.25, 'poor': 0.40}
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key path (e.g., 'defaults.start_date')."""
        keys = key.split('.')
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_default_start_date(self) -> str:
        """Get default start date."""
        return self.get('defaults.start_date', '2024-03-01')
    
    def get_risk_free_rate(self) -> float:
        """Get risk-free rate."""
        return self.get('defaults.risk_free_rate', 0.03)
    
    def get_portfolio_file(self) -> str:
        """Get default portfolio file path."""
        return self.get('defaults.portfolio_file', 'input/input.csv')
    
    def get_threshold(self, metric: str, level: str) -> float:
        """Get threshold value for a metric and level."""
        return self.get(f'thresholds.{metric}.{level}', 0.0)
