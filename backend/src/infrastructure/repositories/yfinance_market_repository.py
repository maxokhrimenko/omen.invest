import yfinance as yf
import pandas as pd
import time
from typing import List, Dict
from ...application.interfaces.repositories import MarketDataRepository
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money
from ..logging.logger_service import get_logger_service
from ..logging.decorators import log_api_call

class YFinanceMarketRepository(MarketDataRepository):
    def __init__(self):
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("infrastructure")
    
    @log_api_call("yfinance", include_request=True, include_response=True)
    def get_price_history(self, tickers: List[Ticker], 
                         date_range: DateRange) -> Dict[Ticker, pd.Series]:
        """Get historical price data for tickers."""
        ticker_symbols = [ticker.symbol for ticker in tickers]
        
        self._logger.info(f"Fetching price history for {len(ticker_symbols)} tickers: {', '.join(ticker_symbols)}")
        self._logger.info(f"Date range: {date_range.start} to {date_range.end}")
        
        try:
            # Download data
            self._logger.debug("Calling yfinance.download()")
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
            self._logger.debug(f"YFinance download completed in {download_duration:.2f}s")
            
            if data.empty:
                self._logger.warning("YFinance returned empty data")
                return {}
            
            self._logger.debug(f"YFinance returned data with shape: {data.shape}")
            result = {}
            
            # Handle single ticker case
            if len(ticker_symbols) == 1:
                ticker = tickers[0]
                self._logger.debug("Processing single ticker data")
                
                if 'Close' in data.columns:
                    prices = data['Close'].dropna()
                    if not prices.empty:
                        result[ticker] = prices
                        self._logger.debug(f"Single ticker data processed: {ticker.symbol} - {len(prices)} data points")
                else:
                    # Multi-level columns even for single ticker
                    symbol = ticker_symbols[0]
                    if (symbol, 'Close') in data.columns:
                        prices = data[symbol]['Close'].dropna()
                        if not prices.empty:
                            result[ticker] = prices
                            self._logger.debug(f"Single ticker data processed (multi-level): {ticker.symbol} - {len(prices)} data points")
            else:
                # Multiple tickers
                self._logger.debug("Processing multiple tickers data")
                for ticker in tickers:
                    symbol = ticker.symbol
                    try:
                        if hasattr(data.columns, 'levels'):
                            # Multi-level columns
                            if symbol in data.columns.levels[0]:
                                prices = data[symbol]['Close'].dropna()
                                if not prices.empty:
                                    result[ticker] = prices
                                    self._logger.debug(f"Multi-ticker data processed: {ticker.symbol} - {len(prices)} data points")
                        else:
                            # Single level columns (fallback)
                            if f"{symbol}_Close" in data.columns:
                                prices = data[f"{symbol}_Close"].dropna()
                                if not prices.empty:
                                    result[ticker] = prices
                                    self._logger.debug(f"Multi-ticker data processed (single-level): {ticker.symbol} - {len(prices)} data points")
                    except (KeyError, AttributeError) as e:
                        # Skip tickers with no data
                        self._logger.warning(f"No data available for ticker {ticker.symbol}: {str(e)}")
                        continue
            
            self._logger.info(f"Successfully processed {len(result)} tickers out of {len(ticker_symbols)} requested")
            self._logger_service.log_api_call(
                "yfinance", 
                "get_price_history", 
                "GET", 
                download_duration, 
                "SUCCESS", 
                {
                    "ticker_count": len(ticker_symbols),
                    "successful_tickers": len(result),
                    "date_range": f"{date_range.start} to {date_range.end}"
                }
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error fetching price data: {str(e)}")
            self._logger_service.log_api_call(
                "yfinance", 
                "get_price_history", 
                "GET", 
                None, 
                "ERROR", 
                {"error": str(e), "ticker_count": len(ticker_symbols)}
            )
            raise ValueError(f"Error fetching price data: {str(e)}")
    
    @log_api_call("yfinance", include_request=True, include_response=True)
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
    
    @log_api_call("yfinance", include_request=True, include_response=True)
    def get_benchmark_data(self, benchmark_symbol: str, 
                          date_range: DateRange) -> pd.Series:
        """Get benchmark data (e.g., S&P 500) for Beta calculation."""
        self._logger.info(f"Fetching benchmark data for {benchmark_symbol}")
        self._logger.info(f"Date range: {date_range.start} to {date_range.end}")
        
        try:
            # Download benchmark data
            self._logger.debug(f"Calling yfinance.download() for benchmark {benchmark_symbol}")
            data = yf.download(
                benchmark_symbol,
                start=date_range.start,
                end=date_range.end,
                progress=False,
                auto_adjust=False
            )
            
            if data.empty:
                self._logger.warning(f"No benchmark data available for {benchmark_symbol}")
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
            
            self._logger.info(f"Retrieved {len(benchmark_prices)} benchmark data points")
            return benchmark_prices
            
        except Exception as e:
            self._logger.error(f"Error fetching benchmark data for {benchmark_symbol}: {str(e)}")
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
