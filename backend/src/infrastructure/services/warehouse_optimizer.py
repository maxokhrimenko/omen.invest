"""
Warehouse optimizer service for database performance.

This service provides optimization capabilities for warehouse operations
including query optimization, connection pooling, and caching strategies.
"""

import sqlite3
import threading
import time
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from datetime import datetime
from ..logging.logger_service import get_logger_service
from ..logging.performance_monitor import get_performance_monitor


class ConnectionPool:
    """Simple connection pool for SQLite connections."""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._pool = []
        self._lock = threading.Lock()
        self._logger = get_logger_service().get_logger("infrastructure")
        
        # Pre-create connections
        for _ in range(min(max_connections, 5)):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            self._pool.append(conn)
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        conn = None
        try:
            with self._lock:
                if self._pool:
                    conn = self._pool.pop()
                else:
                    # Create new connection if pool is empty
                    conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("PRAGMA synchronous=NORMAL")
                    conn.execute("PRAGMA cache_size=10000")
                    conn.execute("PRAGMA temp_store=MEMORY")
            
            yield conn
        finally:
            if conn:
                with self._lock:
                    if len(self._pool) < self.max_connections:
                        self._pool.append(conn)
                    else:
                        conn.close()
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()


class WarehouseOptimizer:
    """Service for optimizing warehouse database operations."""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.connection_pool = ConnectionPool(db_path, max_connections)
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("infrastructure")
        self._performance_monitor = get_performance_monitor()
        
        # Query cache for frequently used queries
        self._query_cache = {}
        self._cache_lock = threading.Lock()
        
        self._logger.info(f"WarehouseOptimizer initialized with {max_connections} max connections")
    
    def optimize_database(self):
        """Optimize database settings and indexes."""
        self._logger.info("Starting database optimization")
        
        with self.connection_pool.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Optimize synchronous mode
            conn.execute("PRAGMA synchronous=NORMAL")
            
            # Increase cache size
            conn.execute("PRAGMA cache_size=10000")
            
            # Use memory for temp tables
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Analyze tables for better query planning
            conn.execute("ANALYZE")
            
            # Create additional indexes for better performance
            self._create_performance_indexes(conn)
            
            conn.commit()
        
        self._logger.info("Database optimization completed")
    
    def _create_performance_indexes(self, conn: sqlite3.Connection):
        """Create additional indexes for better query performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_market_data_ticker_date ON market_data (ticker, date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_date_ticker ON market_data (date, ticker)",
            "CREATE INDEX IF NOT EXISTS idx_dividend_data_ticker_date ON dividend_data (ticker, date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_dividend_data_date_ticker ON dividend_data (date, ticker)",
            "CREATE INDEX IF NOT EXISTS idx_benchmark_data_symbol_date ON benchmark_data (symbol, date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_benchmark_data_date_symbol ON benchmark_data (date, symbol)",
            "CREATE INDEX IF NOT EXISTS idx_dividend_coverage_ticker_dates ON dividend_coverage (ticker, start_date, end_date)",
            "CREATE INDEX IF NOT EXISTS idx_benchmark_coverage_symbol_dates ON benchmark_coverage (symbol, start_date, end_date)"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
                self._logger.debug(f"Created index: {index_sql}")
            except sqlite3.Error as e:
                self._logger.warning(f"Failed to create index: {e}")
    
    def get_price_history_optimized(self, tickers: List[Any], date_range: Any) -> Dict[Any, Any]:
        """Get price history with optimized queries and connection pooling."""
        if not tickers:
            return {}
        
        self._performance_monitor.start_timing("optimized_price_fetch")
        
        ticker_symbols = [t.symbol for t in tickers]
        placeholders = ','.join(['?'] * len(ticker_symbols))
        
        # Use prepared statement for better performance
        query = f"""
            SELECT ticker, date, close_price 
            FROM market_data 
            WHERE ticker IN ({placeholders}) 
            AND date >= ? AND date <= ?
            ORDER BY ticker, date
        """
        
        with self.connection_pool.get_connection() as conn:
            cursor = conn.execute(query, ticker_symbols + [date_range.start.strftime('%Y-%m-%d'), date_range.end.strftime('%Y-%m-%d')])
            
            # Process results into ticker-indexed dictionary
            result = {}
            for ticker in tickers:
                result[ticker] = []
            
            for row in cursor.fetchall():
                ticker_symbol, date_str, price = row
                # Find the ticker object
                ticker_obj = next((t for t in tickers if t.symbol == ticker_symbol), None)
                if ticker_obj is not None:
                    result[ticker_obj].append((date_str, price))
        
        # Convert to pandas Series
        import pandas as pd
        for ticker in result:
            if result[ticker]:
                dates, prices = zip(*result[ticker])
                result[ticker] = pd.Series(prices, index=pd.DatetimeIndex(dates), name='Close')
            else:
                result[ticker] = pd.Series(dtype='float64', name='Close')
        
        fetch_time = self._performance_monitor.end_timing("optimized_price_fetch")
        self._logger.info(f"Optimized price fetch completed in {fetch_time:.3f}s for {len(tickers)} tickers")
        
        return result
    
    def get_dividend_history_optimized(self, tickers: List[Any], date_range: Any) -> Dict[Any, Any]:
        """Get dividend history with optimized queries and connection pooling."""
        if not tickers:
            return {}
        
        self._performance_monitor.start_timing("optimized_dividend_fetch")
        
        ticker_symbols = [t.symbol for t in tickers]
        placeholders = ','.join(['?'] * len(ticker_symbols))
        
        # Use prepared statement for better performance
        query = f"""
            SELECT ticker, date, dividend_amount 
            FROM dividend_data 
            WHERE ticker IN ({placeholders}) 
            AND date >= ? AND date <= ?
            ORDER BY ticker, date
        """
        
        with self.connection_pool.get_connection() as conn:
            cursor = conn.execute(query, ticker_symbols + [date_range.start.strftime('%Y-%m-%d'), date_range.end.strftime('%Y-%m-%d')])
            
            # Process results into ticker-indexed dictionary
            result = {}
            for ticker in tickers:
                result[ticker] = []
            
            for row in cursor.fetchall():
                ticker_symbol, date_str, dividend = row
                # Find the ticker object
                ticker_obj = next((t for t in tickers if t.symbol == ticker_symbol), None)
                if ticker_obj is not None:
                    result[ticker_obj].append((date_str, dividend))
        
        # Convert to pandas Series
        import pandas as pd
        for ticker in result:
            if result[ticker]:
                dates, dividends = zip(*result[ticker])
                result[ticker] = pd.Series(dividends, index=pd.DatetimeIndex(dates), name='Dividends')
            else:
                result[ticker] = pd.Series(dtype='float64', name='Dividends')
        
        fetch_time = self._performance_monitor.end_timing("optimized_dividend_fetch")
        self._logger.info(f"Optimized dividend fetch completed in {fetch_time:.3f}s for {len(tickers)} tickers")
        
        return result
    
    def store_dividend_history(self, ticker: Any, dividend_data: Any) -> None:
        """Store dividend history data in the warehouse."""
        if dividend_data is None or dividend_data.empty:
            return
        
        self._logger.info(f"Storing dividend history for {ticker.symbol} ({len(dividend_data)} records)")
        
        # Prepare data for insertion
        data_to_insert = []
        for date, dividend in dividend_data.items():
            data_to_insert.append((
                ticker.symbol,
                date.strftime('%Y-%m-%d'),
                float(dividend),
                datetime.now().isoformat()
            ))
        
        # Batch insert
        self.batch_insert_optimized("dividend_data", data_to_insert)
        
        # Update coverage
        self._update_dividend_coverage(ticker, dividend_data)
    
    def _update_dividend_coverage(self, ticker: Any, dividend_data: Any) -> None:
        """Update dividend coverage information."""
        if dividend_data is None or dividend_data.empty:
            return
        
        min_date = dividend_data.index.min().strftime('%Y-%m-%d')
        max_date = dividend_data.index.max().strftime('%Y-%m-%d')
        record_count = len(dividend_data)
        
        coverage_data = [(
            ticker.symbol,
            min_date,
            max_date,
            record_count,
            datetime.now().isoformat()
        )]
        
        self.batch_insert_optimized("dividend_coverage", coverage_data)
    
    def batch_insert_optimized(self, table_name: str, data: List[Tuple], batch_size: int = 1000):
        """Insert data in optimized batches with connection pooling."""
        if not data:
            return
        
        self._performance_monitor.start_timing(f"batch_insert_{table_name}")
        
        # Determine column count from first row
        if not data:
            return
        
        column_count = len(data[0])
        placeholders = ','.join(['?'] * column_count)
        
        with self.connection_pool.get_connection() as conn:
            # Use executemany for batch inserts
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                conn.executemany(
                    f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                    batch
                )
            
            conn.commit()
        
        insert_time = self._performance_monitor.end_timing(f"batch_insert_{table_name}")
        self._logger.info(f"Batch insert completed in {insert_time:.3f}s for {len(data)} rows")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the warehouse optimizer."""
        return {
            "max_connections": self.connection_pool.max_connections,
            "active_connections": len(self.connection_pool._pool),
            "active_timings": self._performance_monitor.get_active_timings(),
            "service_type": "warehouse_optimizer"
        }
    
    def close(self):
        """Close the warehouse optimizer and all connections."""
        self.connection_pool.close_all()
        self._logger.info("WarehouseOptimizer closed")


# Global instance
_warehouse_optimizer: Optional[WarehouseOptimizer] = None


def get_warehouse_optimizer(db_path: str = None) -> WarehouseOptimizer:
    """Get or create the global warehouse optimizer service instance."""
    global _warehouse_optimizer
    if _warehouse_optimizer is None:
        if db_path is None:
            from ..config.warehouse_config import WarehouseConfig
            config = WarehouseConfig()
            db_path = config.get_db_path()
        _warehouse_optimizer = WarehouseOptimizer(db_path)
    return _warehouse_optimizer
