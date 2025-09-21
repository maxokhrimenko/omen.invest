from decimal import Decimal
from typing import Union
from ..value_objects.money import Money
from .ticker import Ticker
from ...infrastructure.logging.logger_service import get_logger_service

class Position:
    def __init__(self, ticker: Ticker, quantity: Union[int, float, Decimal]):
        self._ticker = ticker
        self._quantity = Decimal(str(quantity))
        self._validate()
        
        # Log position creation
        logger_service = get_logger_service()
        logger = logger_service.get_logger("domain")
        logger.debug(f"Position created: {ticker.symbol} x {quantity}")
    
    def _validate(self):
        logger_service = get_logger_service()
        logger = logger_service.get_logger("validation")
        
        if self._quantity <= 0:
            logger.error(f"Position validation failed: invalid quantity ({self._quantity}) for {self._ticker.symbol}")
            raise ValueError("Position quantity must be positive")
        
        logger.debug(f"Position validation successful: {self._ticker.symbol} x {self._quantity}")
    
    @property
    def ticker(self) -> Ticker:
        return self._ticker
    
    @property
    def quantity(self) -> Decimal:
        return self._quantity
    
    def get_value(self, price: Money) -> Money:
        logger_service = get_logger_service()
        logger = logger_service.get_logger("calculation")
        
        value = Money(self._quantity * price.amount, price.currency)
        logger.debug(f"Position value calculated: {self._ticker.symbol} x {self._quantity} @ {price} = {value}")
        
        return value
    
    def __str__(self) -> str:
        return f"{self._ticker}: {self._quantity}"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Position) and 
                self._ticker == other._ticker and 
                self._quantity == other._quantity)
    
    def __hash__(self) -> int:
        return hash((self._ticker, self._quantity))
