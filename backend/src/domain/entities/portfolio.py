from typing import List, Dict, Optional
from .position import Position
from .ticker import Ticker
from ..value_objects.money import Money

class Portfolio:
    def __init__(self, positions: List[Position]):
        self._positions = {pos.ticker: pos for pos in positions}
        self._validate()
    
    def _validate(self):
        if not self._positions:
            raise ValueError("Portfolio cannot be empty")
    
    
    def get_position(self, ticker: Ticker) -> Optional[Position]:
        return self._positions.get(ticker)
    
    def get_tickers(self) -> List[Ticker]:
        return list(self._positions.keys())
    
    def get_positions(self) -> List[Position]:
        return list(self._positions.values())
    
    def get_total_value(self, prices: Dict[Ticker, Money]) -> Money:
        total = Money(0)
        
        for ticker, position in self._positions.items():
            if ticker in prices:
                position_value = position.get_value(prices[ticker])
                total = total + position_value
        
        return total
    
    def __len__(self) -> int:
        return len(self._positions)
    
    def __str__(self) -> str:
        return f"Portfolio with {len(self._positions)} positions"
    
    def __iter__(self):
        return iter(self._positions.values())
