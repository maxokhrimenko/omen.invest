from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd
from ...domain.entities.portfolio import Portfolio
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money

class PortfolioRepository(ABC):
    @abstractmethod
    def load(self, file_path: str) -> Portfolio:
        """Load portfolio from file."""
        pass
    
    @abstractmethod
    def save(self, portfolio: Portfolio, file_path: str) -> None:
        """Save portfolio to file."""
        pass

class MarketDataRepository(ABC):
    @abstractmethod
    def get_price_history(self, tickers: List[Ticker], 
                         date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get historical price data for tickers."""
        pass
    
    @abstractmethod
    def get_current_prices(self, tickers: List[Ticker]) -> Dict[Ticker, Money]:
        """Get current prices for tickers."""
        pass
    
    @abstractmethod
    def get_dividend_history(self, ticker: Ticker, 
                           date_range: DateRange) -> pd.Series:
        """Get dividend history for a ticker."""
        pass
