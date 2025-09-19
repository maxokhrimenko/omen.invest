from decimal import Decimal
from typing import Union

class Percentage:
    def __init__(self, value: Union[int, float, Decimal]):
        self._value = Decimal(str(value))
    
    @property
    def value(self) -> Decimal:
        return self._value
    
    def to_decimal(self) -> Decimal:
        return self._value / 100
    
    def to_float(self) -> float:
        return float(self._value)
    
    def format(self) -> str:
        return f"{self._value:.1f}%"
    
    def __str__(self) -> str:
        return self.format()
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Percentage) and self._value == other._value
    
    def __hash__(self):
        return hash(self._value)
