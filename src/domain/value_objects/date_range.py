from datetime import date, datetime
from typing import Union

class DateRange:
    def __init__(self, start: Union[str, date], end: Union[str, date, None] = None):
        self._start = self._parse_date(start)
        self._end = self._parse_date(end) if end else date.today()
        self._validate()
    
    def _parse_date(self, date_input: Union[str, date]) -> date:
        if isinstance(date_input, str):
            return datetime.fromisoformat(date_input).date()
        return date_input
    
    def _validate(self):
        if self._start > self._end:
            raise ValueError("Start date cannot be after end date")
    
    @property
    def start(self) -> date:
        return self._start
    
    @property
    def end(self) -> date:
        return self._end
    
    def __str__(self) -> str:
        return f"{self._start} to {self._end}"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, DateRange) and 
                self._start == other._start and 
                self._end == other._end)
