import sqlite3
import pandas as pd
import os
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime, date
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ..logging.logger_service import get_logger_service
from ..logging.decorators import log_operation
from ..config.warehouse_config import WarehouseConfig


class WarehouseService:
    """Warehouse service for persistent market data storage using SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        # Use provided path or get from configuration
        if db_path is None:
            config = WarehouseConfig()
            self.db_path = config.get_db_path()
        else:
            self.db_path = db_path
            
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("infrastructure")
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure the warehouse directory and database exist."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database with schema
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    ticker TEXT NOT NULL,
                    date TEXT NOT NULL,
                    close_price REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (ticker, date)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dividend_data (
                    ticker TEXT NOT NULL,
                    date TEXT NOT NULL,
                    dividend_amount REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (ticker, date)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dividend_coverage (
                    ticker TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    has_dividends INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (ticker, start_date, end_date)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_data (
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    close_price REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (symbol, date)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_coverage (
                    symbol TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    has_data INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (symbol, start_date, end_date)
                )
            """)
            
            # Create index for efficient queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_date 
                ON market_data (ticker, date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_date 
                ON market_data (date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dividend_ticker_date 
                ON dividend_data (ticker, date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dividend_date 
                ON dividend_data (date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dividend_coverage_ticker 
                ON dividend_coverage (ticker, start_date, end_date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_benchmark_symbol_date 
                ON benchmark_data (symbol, date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_benchmark_date 
                ON benchmark_data (date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_benchmark_coverage_symbol 
                ON benchmark_coverage (symbol, start_date, end_date)
            """)
            
            conn.commit()
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def get_coverage(self, ticker: Ticker, date_range: DateRange) -> Set[str]:
        """Get the set of trading days already stored for a ticker in the given range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date FROM market_data 
                WHERE ticker = ? AND date >= ? AND date <= ?
                ORDER BY date
            """, (ticker.symbol, date_range.start, date_range.end))
            
            return {row[0] for row in cursor.fetchall()}
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def get_missing_ranges(self, ticker: Ticker, date_range: DateRange, 
                          trading_days: Set[str]) -> List[Tuple[str, str]]:
        """Calculate missing trading day ranges that need to be fetched from Yahoo."""
        coverage = self.get_coverage(ticker, date_range)
        
        # Find missing trading days
        missing_days = trading_days - coverage
        
        if not missing_days:
            return []
        
        # Convert to sorted list for range calculation
        missing_days_list = sorted(list(missing_days))
        
        # Group consecutive days into ranges
        ranges = []
        if missing_days_list:
            start = missing_days_list[0]
            end = start
            
            for i in range(1, len(missing_days_list)):
                current = missing_days_list[i]
                # Check if current day is consecutive (allowing for weekends)
                prev_day = pd.Timestamp(missing_days_list[i-1])
                curr_day = pd.Timestamp(current)
                
                # If more than 14 days gap, start a new range (allows for long weekends + holidays)
                if (curr_day - prev_day).days > 14:
                    ranges.append((start, end))
                    start = current
                
                end = current
            
            ranges.append((start, end))
        
        return ranges
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def store_price_data(self, ticker: Ticker, price_data: pd.Series) -> None:
        """Store price data for a ticker in the warehouse."""
        if price_data.empty:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            # Prepare data for insertion
            data_to_insert = []
            created_at = datetime.now().isoformat()
            
            for date_str, price in price_data.items():
                # Convert pandas Timestamp to string if needed
                if hasattr(date_str, 'strftime'):
                    date_str = date_str.strftime('%Y-%m-%d')
                elif isinstance(date_str, str):
                    # Already a string
                    pass
                else:
                    date_str = str(date_str)
                
                data_to_insert.append((
                    ticker.symbol,
                    date_str,
                    float(price),
                    created_at
                ))
            
            # Use INSERT OR REPLACE to handle duplicates
            conn.executemany("""
                INSERT OR REPLACE INTO market_data 
                (ticker, date, close_price, created_at)
                VALUES (?, ?, ?, ?)
            """, data_to_insert)
            
            conn.commit()
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def get_price_data(self, ticker: Ticker, date_range: DateRange) -> pd.Series:
        """Get price data for a ticker from the warehouse."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date, close_price FROM market_data 
                WHERE ticker = ? AND date >= ? AND date <= ?
                ORDER BY date
            """, (ticker.symbol, date_range.start, date_range.end))
            
            rows = cursor.fetchall()
            
            if not rows:
                return pd.Series(dtype='float64', name='Close')
            
            # Convert to pandas Series
            dates = [row[0] for row in rows]
            prices = [row[1] for row in rows]
            
            # Create pandas Series with proper index
            series = pd.Series(prices, index=pd.DatetimeIndex(dates), name='Close')
            return series
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def get_database_size(self) -> int:
        """Get the size of the database file in bytes."""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def store_dividend_data(self, ticker: Ticker, dividend_data: pd.Series, date_range: DateRange) -> None:
        """Store dividend data in the warehouse, including coverage information for periods with no dividends."""
        with sqlite3.connect(self.db_path) as conn:
            current_time = datetime.now().isoformat()
            
            # Store actual dividend data if any exists
            if not dividend_data.empty:
                data_to_insert = []
                for date, dividend_amount in dividend_data.items():
                    # Convert date to string if it's a Timestamp
                    if hasattr(date, 'strftime'):
                        date_str = date.strftime('%Y-%m-%d')
                    else:
                        date_str = str(date)
                    
                    data_to_insert.append((
                        ticker.symbol,
                        date_str,
                        float(dividend_amount),
                        current_time
                    ))
                
                # Insert actual dividend data
                conn.executemany("""
                    INSERT OR REPLACE INTO dividend_data 
                    (ticker, date, dividend_amount, created_at) 
                    VALUES (?, ?, ?, ?)
                """, data_to_insert)
            
            # Store coverage information for the entire date range
            # This ensures we know we've checked this period, even if no dividends were found
            conn.execute("""
                INSERT OR REPLACE INTO dividend_coverage 
                (ticker, start_date, end_date, has_dividends, created_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (
                ticker.symbol,
                date_range.start.strftime('%Y-%m-%d'),
                date_range.end.strftime('%Y-%m-%d'),
                1 if not dividend_data.empty else 0,  # 1 if dividends exist, 0 if none
                current_time
            ))
            conn.commit()
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def get_dividend_data(self, ticker: Ticker, date_range: DateRange) -> pd.Series:
        """Get dividend data from the warehouse."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date, dividend_amount 
                FROM dividend_data 
                WHERE ticker = ? AND date >= ? AND date <= ?
                ORDER BY date
            """, (ticker.symbol, date_range.start.strftime('%Y-%m-%d'), 
                  date_range.end.strftime('%Y-%m-%d')))
            
            rows = cursor.fetchall()
            
            if not rows:
                return pd.Series(dtype='float64', name='Dividends')
            
            # Convert to pandas Series
            dates = [row[0] for row in rows]
            dividends = [row[1] for row in rows]
            
            # Create pandas Series with proper index
            series = pd.Series(dividends, index=pd.DatetimeIndex(dates), name='Dividends')
            return series
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def get_dividend_coverage(self, ticker: Ticker, date_range: DateRange) -> Set[str]:
        """Get dividend coverage for a ticker in the given date range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date 
                FROM dividend_data 
                WHERE ticker = ? AND date >= ? AND date <= ?
            """, (ticker.symbol, date_range.start.strftime('%Y-%m-%d'), 
                  date_range.end.strftime('%Y-%m-%d')))
            
            rows = cursor.fetchall()
            return {row[0] for row in rows}
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def has_dividend_coverage(self, ticker: Ticker, date_range: DateRange) -> bool:
        """Check if we have dividend coverage information for a ticker in the given date range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 1 
                FROM dividend_coverage 
                WHERE ticker = ? AND start_date <= ? AND end_date >= ?
                LIMIT 1
            """, (ticker.symbol, 
                  date_range.start.strftime('%Y-%m-%d'),
                  date_range.end.strftime('%Y-%m-%d')))
            
            return cursor.fetchone() is not None
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def store_benchmark_data(self, symbol: str, benchmark_data, date_range: DateRange) -> None:
        """Store benchmark data in the warehouse, including coverage information."""
        if benchmark_data.empty:
            return
        
        # Convert DataFrame to Series if needed
        if isinstance(benchmark_data, pd.DataFrame):
            if 'Close' in benchmark_data.columns:
                benchmark_data = benchmark_data['Close']
            elif symbol in benchmark_data.columns:
                benchmark_data = benchmark_data[symbol]
            else:
                # Take the first column if it's a single-column DataFrame
                benchmark_data = benchmark_data.iloc[:, 0]
        
        if benchmark_data.empty:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            current_time = datetime.now().isoformat()
            
            # Store actual benchmark data
            data_to_insert = []
            # Use items() for pandas Series to get (index, value) pairs
            for date, price in benchmark_data.items():
                # Convert date to string if it's a Timestamp
                if hasattr(date, 'strftime'):
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = str(date)
                
                # Handle price - it might be a scalar or a Series
                if hasattr(price, 'iloc'):
                    # If it's a Series, take the first value (usually Close price)
                    price_value = float(price.iloc[0]) if not price.empty else 0.0
                else:
                    # If it's a scalar, convert to float
                    price_value = float(price)
                
                data_to_insert.append((
                    symbol,
                    date_str,
                    price_value,
                    current_time
                ))
            
            # Insert benchmark data
            conn.executemany("""
                INSERT OR REPLACE INTO benchmark_data 
                (symbol, date, close_price, created_at) 
                VALUES (?, ?, ?, ?)
            """, data_to_insert)
            
            # Store coverage information for the entire date range
            conn.execute("""
                INSERT OR REPLACE INTO benchmark_coverage 
                (symbol, start_date, end_date, has_data, created_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (
                symbol,
                date_range.start.strftime('%Y-%m-%d'),
                date_range.end.strftime('%Y-%m-%d'),
                1,  # 1 if data exists
                current_time
            ))
            conn.commit()
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def get_benchmark_data(self, symbol: str, date_range: DateRange) -> pd.Series:
        """Get benchmark data from the warehouse."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date, close_price 
                FROM benchmark_data 
                WHERE symbol = ? AND date >= ? AND date <= ?
                ORDER BY date
            """, (symbol, date_range.start.strftime('%Y-%m-%d'), 
                  date_range.end.strftime('%Y-%m-%d')))
            
            rows = cursor.fetchall()
            
            if not rows:
                return pd.Series(dtype='float64', name='Close')
            
            # Convert to pandas Series
            dates = [row[0] for row in rows]
            prices = [row[1] for row in rows]
            
            # Create pandas Series with proper index
            series = pd.Series(prices, index=pd.DatetimeIndex(dates), name='Close')
            return series
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def has_benchmark_coverage(self, symbol: str, date_range: DateRange) -> bool:
        """Check if we have benchmark coverage information for a symbol in the given date range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 1 
                FROM benchmark_coverage 
                WHERE symbol = ? AND start_date <= ? AND end_date >= ?
                LIMIT 1
            """, (symbol, 
                  date_range.start.strftime('%Y-%m-%d'),
                  date_range.end.strftime('%Y-%m-%d')))
            
            return cursor.fetchone() is not None
    
    @log_operation("warehouse", include_args=True, include_result=True)
    def clear_data(self, ticker: Optional[Ticker] = None) -> None:
        """Clear data for a specific ticker or all data."""
        with sqlite3.connect(self.db_path) as conn:
            if ticker:
                conn.execute("DELETE FROM market_data WHERE ticker = ?", (ticker.symbol,))
                conn.execute("DELETE FROM dividend_data WHERE ticker = ?", (ticker.symbol,))
                conn.execute("DELETE FROM dividend_coverage WHERE ticker = ?", (ticker.symbol,))
            else:
                conn.execute("DELETE FROM market_data")
                conn.execute("DELETE FROM dividend_data")
                conn.execute("DELETE FROM dividend_coverage")
                conn.execute("DELETE FROM benchmark_data")
                conn.execute("DELETE FROM benchmark_coverage")
            conn.commit()
