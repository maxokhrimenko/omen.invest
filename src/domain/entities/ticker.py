from ...infrastructure.logging.logger_service import get_logger_service


class Ticker:
    def __init__(self, symbol: str):
        self._symbol = symbol.upper().strip()
        self._validate()
        
        # Log ticker creation
        logger_service = get_logger_service()
        logger = logger_service.get_logger("domain")
        logger.debug(f"Ticker created: {self._symbol}")
    
    def _validate(self):
        logger_service = get_logger_service()
        logger = logger_service.get_logger("validation")
        
        if not self._symbol:
            logger.error("Ticker validation failed: empty symbol")
            raise ValueError("Ticker symbol cannot be empty")
        if len(self._symbol) > 10:
            logger.error(f"Ticker validation failed: symbol too long ({len(self._symbol)} chars): {self._symbol}")
            raise ValueError("Ticker symbol too long")
        
        logger.debug(f"Ticker validation successful: {self._symbol}")
    
    @property
    def symbol(self) -> str:
        return self._symbol
    
    def __str__(self) -> str:
        return self._symbol
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Ticker) and self._symbol == other._symbol
    
    def __hash__(self) -> int:
        return hash(self._symbol)
    
    def __repr__(self) -> str:
        return f"Ticker('{self._symbol}')"
