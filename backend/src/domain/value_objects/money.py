from decimal import Decimal
from typing import Union

class Money:
    def __init__(self, amount: Union[int, float, Decimal], currency: str = "USD"):
        self._amount = Decimal(str(amount))
        self._currency = currency
        self._validate()
    
    def _validate(self):
        if self._amount < 0:
            raise ValueError("Money amount cannot be negative")
    
    @property
    def amount(self) -> Decimal:
        return self._amount
    
    @property 
    def currency(self) -> str:
        return self._currency
    
    def __str__(self) -> str:
        return f"${self._amount:.2f}"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Money) and 
                self._amount == other._amount and 
                self._currency == other._currency)
    
    def __add__(self, other):
        if isinstance(other, Money):
            if self._currency != other._currency:
                raise ValueError("Cannot add different currencies")
            result = Money(self._amount + other._amount, self._currency)
            return result
        result = Money(self._amount + Decimal(str(other)), self._currency)
        return result
    
    def __mul__(self, other):
        result = Money(self._amount * Decimal(str(other)), self._currency)
        return result
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __hash__(self):
        return hash((self._amount, self._currency))
