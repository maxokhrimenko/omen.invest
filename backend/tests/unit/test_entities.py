import pytest
from decimal import Decimal
from src.domain.entities.ticker import Ticker
from src.domain.entities.position import Position
from src.domain.entities.portfolio import Portfolio
from src.domain.value_objects.money import Money

class TestTicker:
    def test_creation_with_valid_symbol(self):
        ticker = Ticker("AAPL")
        assert ticker.symbol == "AAPL"
    
    def test_symbol_normalization(self):
        ticker = Ticker("  aapl  ")
        assert ticker.symbol == "AAPL"
    
    def test_empty_symbol_raises_error(self):
        with pytest.raises(ValueError, match="Ticker symbol cannot be empty"):
            Ticker("")
    
    def test_long_symbol_raises_error(self):
        with pytest.raises(ValueError, match="Ticker symbol too long"):
            Ticker("VERYLONGTICKER")
    
    def test_equality(self):
        ticker1 = Ticker("AAPL")
        ticker2 = Ticker("AAPL")
        ticker3 = Ticker("MSFT")
        
        assert ticker1 == ticker2
        assert ticker1 != ticker3
    
    def test_hash(self):
        ticker1 = Ticker("AAPL")
        ticker2 = Ticker("AAPL")
        
        assert hash(ticker1) == hash(ticker2)
    
    def test_string_representation(self):
        ticker = Ticker("AAPL")
        assert str(ticker) == "AAPL"

class TestPosition:
    def test_creation_with_valid_data(self):
        ticker = Ticker("AAPL")
        position = Position(ticker, 10)
        
        assert position.ticker == ticker
        assert position.quantity == Decimal('10')
    
    def test_zero_quantity_raises_error(self):
        ticker = Ticker("AAPL")
        with pytest.raises(ValueError, match="Position quantity must be positive"):
            Position(ticker, 0)
    
    def test_negative_quantity_raises_error(self):
        ticker = Ticker("AAPL")
        with pytest.raises(ValueError, match="Position quantity must be positive"):
            Position(ticker, -5)
    
    def test_get_value(self):
        ticker = Ticker("AAPL")
        position = Position(ticker, 10)
        price = Money(150)
        
        value = position.get_value(price)
        assert value.amount == Decimal('1500')
    
    def test_string_representation(self):
        ticker = Ticker("AAPL")
        position = Position(ticker, 10.5)
        
        assert str(position) == "AAPL: 10.5"

class TestPortfolio:
    def test_creation_with_positions(self):
        ticker1 = Ticker("AAPL")
        ticker2 = Ticker("MSFT")
        position1 = Position(ticker1, 10)
        position2 = Position(ticker2, 5)
        
        portfolio = Portfolio([position1, position2])
        
        assert len(portfolio) == 2
        assert portfolio.get_position(ticker1) == position1
        assert portfolio.get_position(ticker2) == position2
    
    def test_empty_portfolio_raises_error(self):
        with pytest.raises(ValueError, match="Portfolio cannot be empty"):
            Portfolio([])
    
    def test_get_tickers(self):
        ticker1 = Ticker("AAPL")
        ticker2 = Ticker("MSFT")
        position1 = Position(ticker1, 10)
        position2 = Position(ticker2, 5)
        
        portfolio = Portfolio([position1, position2])
        tickers = portfolio.get_tickers()
        
        assert len(tickers) == 2
        assert ticker1 in tickers
        assert ticker2 in tickers
    
    def test_add_position(self):
        ticker1 = Ticker("AAPL")
        position1 = Position(ticker1, 10)
        
        portfolio = Portfolio([position1])
        
        ticker2 = Ticker("MSFT")
        position2 = Position(ticker2, 5)
        portfolio.add_position(position2)
        
        assert len(portfolio) == 2
        assert portfolio.get_position(ticker2) == position2
    
    def test_get_total_value(self):
        ticker1 = Ticker("AAPL")
        ticker2 = Ticker("MSFT")
        position1 = Position(ticker1, 10)
        position2 = Position(ticker2, 5)
        
        portfolio = Portfolio([position1, position2])
        
        prices = {
            ticker1: Money(150),
            ticker2: Money(250)
        }
        
        total_value = portfolio.get_total_value(prices)
        # 10 * 150 + 5 * 250 = 1500 + 1250 = 2750
        assert total_value.amount == Decimal('2750')
    
    def test_iteration(self):
        ticker1 = Ticker("AAPL")
        ticker2 = Ticker("MSFT")
        position1 = Position(ticker1, 10)
        position2 = Position(ticker2, 5)
        
        portfolio = Portfolio([position1, position2])
        
        positions = list(portfolio)
        assert len(positions) == 2
        assert position1 in positions
        assert position2 in positions
