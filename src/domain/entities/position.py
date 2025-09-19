from decimal import Decimal
from typing import Union
from ..value_objects.money import Money
from .ticker import Ticker

class Position:
    def __init__(self, ticker: Ticker, quantity: Union[int, float, Decimal]):
        self._ticker = ticker
        self._quantity = Decimal(str(quantity))
        self._validate()
    
    def _validate(self):
        if self._quantity <= 0:
            raise ValueError("Position quantity must be positive")
    
    @property
    def ticker(self) -> Ticker:
        return self._ticker
    
    @property
    def quantity(self) -> Decimal:
        return self._quantity
    
    def get_value(self, price: Money) -> Money:
        return Money(self._quantity * price.amount, price.currency)
    
    def __str__(self) -> str:
        return f"{self._ticker}: {self._quantity}"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Position) and 
                self._ticker == other._ticker and 
                self._quantity == other._quantity)
    
    def __hash__(self) -> int:
        return hash((self._ticker, self._quantity))
