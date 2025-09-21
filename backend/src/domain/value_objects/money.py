from decimal import Decimal
from typing import Union
from ...infrastructure.logging.logger_service import get_logger_service

class Money:
    def __init__(self, amount: Union[int, float, Decimal], currency: str = "USD"):
        self._amount = Decimal(str(amount))
        self._currency = currency
        self._validate()
        
        # Log money creation for significant amounts
        logger_service = get_logger_service()
        logger = logger_service.get_logger("domain")
        if float(self._amount) >= 1000:  # Log only significant amounts
            logger.debug(f"Money created: {self._amount} {self._currency}")
    
    def _validate(self):
        logger_service = get_logger_service()
        logger = logger_service.get_logger("validation")
        
        if self._amount < 0:
            logger.error(f"Money validation failed: negative amount ({self._amount})")
            raise ValueError("Money amount cannot be negative")
        
        logger.debug(f"Money validation successful: {self._amount} {self._currency}")
    
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
        logger_service = get_logger_service()
        logger = logger_service.get_logger("calculation")
        
        if isinstance(other, Money):
            if self._currency != other._currency:
                logger.error(f"Money addition failed: currency mismatch ({self._currency} + {other._currency})")
                raise ValueError("Cannot add different currencies")
            result = Money(self._amount + other._amount, self._currency)
            logger.debug(f"Money addition: {self._amount} {self._currency} + {other._amount} {other._currency} = {result._amount} {result._currency}")
            return result
        result = Money(self._amount + Decimal(str(other)), self._currency)
        logger.debug(f"Money addition: {self._amount} {self._currency} + {other} = {result._amount} {result._currency}")
        return result
    
    def __mul__(self, other):
        logger_service = get_logger_service()
        logger = logger_service.get_logger("calculation")
        
        result = Money(self._amount * Decimal(str(other)), self._currency)
        logger.debug(f"Money multiplication: {self._amount} {self._currency} * {other} = {result._amount} {result._currency}")
        return result
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __hash__(self):
        return hash((self._amount, self._currency))
