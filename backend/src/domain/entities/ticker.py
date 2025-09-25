class Ticker:
    def __init__(self, symbol: str):
        self._symbol = symbol.upper().strip()
        self._validate()
    
    def _validate(self):
        if not self._symbol:
            raise ValueError("Ticker symbol cannot be empty")
        if len(self._symbol) > 10:
            raise ValueError("Ticker symbol too long")
    
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
