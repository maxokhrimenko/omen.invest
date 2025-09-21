from typing import List, Dict, Optional
from .position import Position
from .ticker import Ticker
from ..value_objects.money import Money
from ...infrastructure.logging.logger_service import get_logger_service

class Portfolio:
    def __init__(self, positions: List[Position]):
        self._positions = {pos.ticker: pos for pos in positions}
        self._validate()
        
        # Log portfolio creation
        logger_service = get_logger_service()
        logger = logger_service.get_logger("domain")
        ticker_symbols = [pos.ticker.symbol for pos in positions]
        logger.info(f"Portfolio created with {len(positions)} positions: {', '.join(ticker_symbols)}")
    
    def _validate(self):
        logger_service = get_logger_service()
        logger = logger_service.get_logger("validation")
        
        if not self._positions:
            logger.error("Portfolio validation failed: empty portfolio")
            raise ValueError("Portfolio cannot be empty")
        
        logger.debug(f"Portfolio validation successful: {len(self._positions)} positions")
    
    def add_position(self, position: Position) -> None:
        self._positions[position.ticker] = position
    
    def get_position(self, ticker: Ticker) -> Optional[Position]:
        return self._positions.get(ticker)
    
    def get_tickers(self) -> List[Ticker]:
        return list(self._positions.keys())
    
    def get_positions(self) -> List[Position]:
        return list(self._positions.values())
    
    def get_total_value(self, prices: Dict[Ticker, Money]) -> Money:
        logger_service = get_logger_service()
        logger = logger_service.get_logger("calculation")
        
        total = Money(0)
        calculated_positions = 0
        missing_prices = []
        
        for ticker, position in self._positions.items():
            if ticker in prices:
                position_value = position.get_value(prices[ticker])
                total = total + position_value
                calculated_positions += 1
            else:
                missing_prices.append(ticker.symbol)
        
        logger.info(f"Portfolio total value calculated: {total} (calculated {calculated_positions}/{len(self._positions)} positions)")
        if missing_prices:
            logger.warning(f"Missing prices for tickers: {', '.join(missing_prices)}")
        
        return total
    
    def __len__(self) -> int:
        return len(self._positions)
    
    def __str__(self) -> str:
        return f"Portfolio with {len(self._positions)} positions"
    
    def __iter__(self):
        return iter(self._positions.values())
