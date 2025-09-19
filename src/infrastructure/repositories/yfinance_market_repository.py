import yfinance as yf
import pandas as pd
from typing import List, Dict
from ...application.interfaces.repositories import MarketDataRepository
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money

class YFinanceMarketRepository(MarketDataRepository):
    def get_price_history(self, tickers: List[Ticker], 
                         date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get historical price data for tickers."""
        ticker_symbols = [ticker.symbol for ticker in tickers]
        
        try:
            # Download data
            data = yf.download(
                ticker_symbols,
                start=date_range.start,
                end=date_range.end,
                auto_adjust=True,
                progress=False,
                group_by="ticker"
            )
            
            if data.empty:
                return {}
            
            result = {}
            
            # Handle single ticker case
            if len(ticker_symbols) == 1:
                ticker = tickers[0]
                if 'Close' in data.columns:
                    prices = data['Close'].dropna()
                    if not prices.empty:
                        result[ticker] = prices
                else:
                    # Multi-level columns even for single ticker
                    symbol = ticker_symbols[0]
                    if (symbol, 'Close') in data.columns:
                        prices = data[symbol]['Close'].dropna()
                        if not prices.empty:
                            result[ticker] = prices
            else:
                # Multiple tickers
                for ticker in tickers:
                    symbol = ticker.symbol
                    try:
                        if hasattr(data.columns, 'levels'):
                            # Multi-level columns
                            if symbol in data.columns.levels[0]:
                                prices = data[symbol]['Close'].dropna()
                                if not prices.empty:
                                    result[ticker] = prices
                        else:
                            # Single level columns (fallback)
                            if f"{symbol}_Close" in data.columns:
                                prices = data[f"{symbol}_Close"].dropna()
                                if not prices.empty:
                                    result[ticker] = prices
                    except (KeyError, AttributeError):
                        # Skip tickers with no data
                        continue
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error fetching price data: {str(e)}")
    
    def get_current_prices(self, tickers: List[Ticker]) -> Dict[Ticker, Money]:
        """Get current prices for tickers."""
        ticker_symbols = [ticker.symbol for ticker in tickers]
        
        try:
            result = {}
            
            for ticker in tickers:
                ticker_obj = yf.Ticker(ticker.symbol)
                info = ticker_obj.info
                
                # Try different price fields
                current_price = None
                price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose']
                
                for field in price_fields:
                    if field in info and info[field] is not None:
                        current_price = float(info[field])
                        break
                
                if current_price is not None and current_price > 0:
                    result[ticker] = Money(current_price)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error fetching current prices: {str(e)}")
    
    def get_dividend_history(self, ticker: Ticker, 
                           date_range: DateRange) -> pd.Series:
        """Get dividend history for a ticker."""
        try:
            ticker_obj = yf.Ticker(ticker.symbol)
            dividends = ticker_obj.dividends
            
            if dividends.empty:
                return pd.Series(dtype='float64', name='Dividends')
            
            # Filter by date range
            start_timestamp = pd.Timestamp(date_range.start)
            end_timestamp = pd.Timestamp(date_range.end)
            
            # Convert timezone-aware timestamps to timezone-naive if needed
            if dividends.index.tz is not None:
                dividends.index = dividends.index.tz_localize(None)
            
            filtered_dividends = dividends[
                (dividends.index >= start_timestamp) & 
                (dividends.index <= end_timestamp)
            ]
            
            return filtered_dividends
            
        except Exception as e:
            # Return empty series instead of raising error for individual ticker failures
            return pd.Series(dtype='float64', name='Dividends')
    
    def get_ticker_info(self, ticker: Ticker) -> Dict:
        """Get additional ticker information."""
        try:
            ticker_obj = yf.Ticker(ticker.symbol)
            return ticker_obj.info
        except Exception:
            return {}
