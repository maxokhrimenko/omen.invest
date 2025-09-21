import pytest
from decimal import Decimal
from datetime import date
from src.domain.value_objects.money import Money
from src.domain.value_objects.percentage import Percentage
from src.domain.value_objects.date_range import DateRange

class TestMoney:
    def test_creation_with_valid_amount(self):
        money = Money(100.50)
        assert money.amount == Decimal('100.50')
        assert money.currency == "USD"
    
    def test_creation_with_negative_amount_raises_error(self):
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            Money(-10)
    
    def test_string_representation(self):
        money = Money(100.50)
        assert str(money) == "$100.50"
    
    def test_equality(self):
        money1 = Money(100.50)
        money2 = Money(100.50)
        money3 = Money(100.51)
        
        assert money1 == money2
        assert money1 != money3
    
    def test_addition(self):
        money1 = Money(100)
        money2 = Money(50)
        result = money1 + money2
        
        assert result.amount == Decimal('150')
        assert result.currency == "USD"
    
    def test_multiplication(self):
        money = Money(100)
        result = money * 2
        
        assert result.amount == Decimal('200')
        assert result.currency == "USD"

class TestPercentage:
    def test_creation(self):
        pct = Percentage(50.5)
        assert pct.value == Decimal('50.5')
    
    def test_to_decimal(self):
        pct = Percentage(50)
        assert pct.to_decimal() == Decimal('0.5')
    
    def test_to_float(self):
        pct = Percentage(25.5)
        assert pct.to_float() == 25.5
    
    def test_format(self):
        pct = Percentage(25.67)
        assert pct.format() == "25.7%"
    
    def test_string_representation(self):
        pct = Percentage(30.1)
        assert str(pct) == "30.1%"

class TestDateRange:
    def test_creation_with_dates(self):
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        date_range = DateRange(start, end)
        
        assert date_range.start == start
        assert date_range.end == end
    
    def test_creation_with_strings(self):
        date_range = DateRange("2024-01-01", "2024-12-31")
        
        assert date_range.start == date(2024, 1, 1)
        assert date_range.end == date(2024, 12, 31)
    
    def test_creation_without_end_date(self):
        date_range = DateRange("2024-01-01")
        
        assert date_range.start == date(2024, 1, 1)
        assert date_range.end == date.today()
    
    def test_invalid_date_range_raises_error(self):
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            DateRange("2024-12-31", "2024-01-01")
    
    def test_string_representation(self):
        date_range = DateRange("2024-01-01", "2024-12-31")
        expected = "2024-01-01 to 2024-12-31"
        assert str(date_range) == expected
