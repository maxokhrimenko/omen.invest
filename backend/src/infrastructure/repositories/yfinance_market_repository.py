import yfinance as yf
import pandas as pd
import time
from typing import List, Dict
from ...application.interfaces.repositories import MarketDataRepository
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money

class YFinanceMarketRepository(MarketDataRepository):
    def __init__(self):
        pass
    
    def get_price_history(self, tickers: List[Ticker], 
                         date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get historical price data for tickers."""
        ticker_symbols = [ticker.symbol for ticker in tickers]
        
        try:
            # Download data
            start_time = time.time()
            
            data = yf.download(
                ticker_symbols,
                start=date_range.start,
                end=date_range.end,
                auto_adjust=True,
                progress=False,
                group_by="ticker"
            )
            
            download_duration = time.time() - start_time
            
            if data.empty:
                return {}
            
            result = {}
            
            # Handle both single and multiple ticker cases
            for ticker in tickers:
                symbol = ticker.symbol
                try:
                    # Check for multi-level columns (most common case)
                    if hasattr(data.columns, 'levels') and len(data.columns.levels) > 1:
                        # Multi-level columns: (symbol, 'Close')
                        if symbol in data.columns.levels[0] and 'Close' in data.columns.levels[1]:
                            prices = data[symbol]['Close'].dropna()
                            if not prices.empty:
                                result[ticker] = prices
                    else:
                        # Single level columns
                        if 'Close' in data.columns:
                            # Single ticker case
                            prices = data['Close'].dropna()
                            if not prices.empty:
                                result[ticker] = prices
                        elif f"{symbol}_Close" in data.columns:
                            # Multiple tickers with underscore format
                            prices = data[f"{symbol}_Close"].dropna()
                            if not prices.empty:
                                result[ticker] = prices
                except (KeyError, AttributeError, IndexError) as e:
                    # Skip tickers with no data
                    print(f"Warning: No data found for {symbol}: {e}")
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
    
    def get_benchmark_data(self, benchmark_symbol: str, 
                          date_range: DateRange) -> pd.Series:
        """Get benchmark data (e.g., S&P 500) for Beta calculation."""
        try:
            # Download benchmark data
            data = yf.download(
                benchmark_symbol,
                start=date_range.start,
                end=date_range.end,
                progress=False,
                auto_adjust=False
            )
            
            if data.empty:
                return pd.Series(dtype=float)
            
            # Extract closing prices
            if 'Close' in data.columns:
                benchmark_prices = data['Close']
            elif ('Close', benchmark_symbol) in data.columns:
                # Handle multi-level columns for single symbol
                benchmark_prices = data[('Close', benchmark_symbol)]
            else:
                # Handle case where data is a Series instead of DataFrame
                benchmark_prices = data
            
            # Ensure we return a Series, not a DataFrame
            if isinstance(benchmark_prices, pd.DataFrame):
                # If it's a DataFrame, take the first column and convert to Series
                benchmark_prices = benchmark_prices.iloc[:, 0]
            
            return benchmark_prices
            
        except Exception as e:
            raise ValueError(f"Error fetching benchmark data: {str(e)}")
    
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
