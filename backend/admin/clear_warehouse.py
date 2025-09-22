#!/usr/bin/env python3
"""
Warehouse Clear Script - Administrative tool for clearing warehouse data.
Version 4.4.3 - Portfolio Analysis & Visualization

This script provides functionality to:
- Clear all warehouse data
- Clear data for specific tickers
- Clear benchmark data (S&P 500, NASDAQ)
- Show warehouse statistics including benchmark data
- Backup warehouse data before clearing (optional)
- Reset warehouse metrics

Usage:
    python backend/admin/clear_warehouse.py --help
    python backend/admin/clear_warehouse.py --clear-all
    python backend/admin/clear_warehouse.py --clear-ticker AAPL
    python backend/admin/clear_warehouse.py --clear-benchmarks
    python backend/admin/clear_warehouse.py --stats
    python backend/admin/clear_warehouse.py --backup-and-clear
    python backend/admin/clear_warehouse.py --reset-metrics
"""

import os
import sys
import shutil
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from src.infrastructure.warehouse.warehouse_service import WarehouseService
    from src.infrastructure.config.warehouse_config import WarehouseConfig
except ImportError:
    # Fallback: create minimal classes if imports fail
    class WarehouseService:
        def __init__(self, db_path: str):
            self.db_path = db_path
        
        def clear_data(self, ticker=None):
            if not os.path.exists(self.db_path):
                return
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
    
    class WarehouseConfig:
        def __init__(self):
            self.enabled = True
            self.db_path = "../database/warehouse/warehouse.sqlite"


class WarehouseClearManager:
    """Manager for clearing and managing warehouse data."""
    
    def __init__(self, warehouse_db_path: str = "../database/warehouse/warehouse.sqlite"):
        # Use relative path from the script location
        # Get the script directory and resolve relative to project root
        script_path = Path(__file__)
        # Find project root by looking for common project files
        current = script_path.parent
        while current != current.parent:
            if (current / "package.json").exists() or (current / "README.md").exists():
                break
            current = current.parent
        
        # Use the found project root
        self.warehouse_db_path = current / warehouse_db_path
        self.backup_dir = self.warehouse_db_path.parent / "backups"
        self.warehouse_service = WarehouseService(str(self.warehouse_db_path))
        self.config = WarehouseConfig()
    
    def get_warehouse_statistics(self) -> Dict[str, Any]:
        """Get statistics about current warehouse data."""
        stats = {
            "database_exists": False,
            "database_size": 0,
            "tickers": [],
            "total_records": 0,
            "date_range": {"earliest": None, "latest": None},
            "storage_breakdown": {}
        }
        
        if not self.warehouse_db_path.exists():
            return stats
        
        stats["database_exists"] = True
        stats["database_size"] = self.warehouse_db_path.stat().st_size
        
        try:
            with sqlite3.connect(self.warehouse_db_path) as conn:
                # Get price data statistics
                cursor = conn.execute("""
                    SELECT ticker, COUNT(*) as record_count, 
                           MIN(date) as earliest_date, MAX(date) as latest_date
                    FROM market_data 
                    GROUP BY ticker
                    ORDER BY ticker
                """)
                
                price_data = cursor.fetchall()
                
                # Get dividend data statistics
                cursor = conn.execute("""
                    SELECT ticker, COUNT(*) as record_count, 
                           MIN(date) as earliest_date, MAX(date) as latest_date
                    FROM dividend_data 
                    GROUP BY ticker
                    ORDER BY ticker
                """)
                
                dividend_data = cursor.fetchall()
                
                # Get dividend coverage statistics
                cursor = conn.execute("""
                    SELECT ticker, COUNT(*) as coverage_count, 
                           MIN(start_date) as earliest_coverage, MAX(end_date) as latest_coverage
                    FROM dividend_coverage 
                    GROUP BY ticker
                    ORDER BY ticker
                """)
                
                dividend_coverage = cursor.fetchall()
                
                # Get benchmark data statistics
                cursor = conn.execute("""
                    SELECT symbol, COUNT(*) as record_count, 
                           MIN(date) as earliest_date, MAX(date) as latest_date
                    FROM benchmark_data 
                    GROUP BY symbol
                    ORDER BY symbol
                """)
                
                benchmark_data = cursor.fetchall()
                
                # Get benchmark coverage statistics
                cursor = conn.execute("""
                    SELECT symbol, COUNT(*) as coverage_count, 
                           MIN(start_date) as earliest_coverage, MAX(end_date) as latest_coverage
                    FROM benchmark_coverage 
                    GROUP BY symbol
                    ORDER BY symbol
                """)
                
                benchmark_coverage = cursor.fetchall()
                
                # Combine price, dividend, coverage, and benchmark data
                all_tickers = set()
                price_stats = {}
                dividend_stats = {}
                coverage_stats = {}
                benchmark_stats = {}
                benchmark_coverage_stats = {}
                
                for ticker, count, earliest, latest in price_data:
                    all_tickers.add(ticker)
                    price_stats[ticker] = {
                        "records": count,
                        "earliest_date": earliest,
                        "latest_date": latest
                    }
                
                for ticker, count, earliest, latest in dividend_data:
                    all_tickers.add(ticker)
                    dividend_stats[ticker] = {
                        "records": count,
                        "earliest_date": earliest,
                        "latest_date": latest
                    }
                
                for ticker, count, earliest, latest in dividend_coverage:
                    all_tickers.add(ticker)
                    coverage_stats[ticker] = {
                        "coverage_periods": count,
                        "earliest_coverage": earliest,
                        "latest_coverage": latest
                    }
                
                for symbol, count, earliest, latest in benchmark_data:
                    benchmark_stats[symbol] = {
                        "records": count,
                        "earliest_date": earliest,
                        "latest_date": latest
                    }
                
                for symbol, count, earliest, latest in benchmark_coverage:
                    benchmark_coverage_stats[symbol] = {
                        "coverage_periods": count,
                        "earliest_coverage": earliest,
                        "latest_coverage": latest
                    }
                
                stats["tickers"] = sorted(list(all_tickers))
                stats["total_records"] = (sum(row[1] for row in price_data) + 
                                        sum(row[1] for row in dividend_data) + 
                                        sum(row[1] for row in benchmark_data))
                stats["benchmark_symbols"] = list(benchmark_stats.keys())
                
                # Storage breakdown by ticker
                for ticker in all_tickers:
                    price_info = price_stats.get(ticker, {"records": 0, "earliest_date": None, "latest_date": None})
                    dividend_info = dividend_stats.get(ticker, {"records": 0, "earliest_date": None, "latest_date": None})
                    coverage_info = coverage_stats.get(ticker, {"coverage_periods": 0, "earliest_coverage": None, "latest_coverage": None})
                    
                    stats["storage_breakdown"][ticker] = {
                        "price_records": price_info["records"],
                        "dividend_records": dividend_info["records"],
                        "dividend_coverage_periods": coverage_info["coverage_periods"],
                        "total_records": price_info["records"] + dividend_info["records"],
                        "price_range": f"{price_info['earliest_date']} to {price_info['latest_date']}" if price_info['earliest_date'] else "No price data",
                        "dividend_range": f"{dividend_info['earliest_date']} to {dividend_info['latest_date']}" if dividend_info['earliest_date'] else "No dividend data",
                        "dividend_coverage_range": f"{coverage_info['earliest_coverage']} to {coverage_info['latest_coverage']}" if coverage_info['earliest_coverage'] else "No dividend coverage"
                    }
                
                # Overall date range
                all_earliest = []
                all_latest = []
                
                for ticker in all_tickers:
                    price_info = price_stats.get(ticker, {"earliest_date": None, "latest_date": None})
                    dividend_info = dividend_stats.get(ticker, {"earliest_date": None, "latest_date": None})
                    
                    if price_info["earliest_date"]:
                        all_earliest.append(price_info["earliest_date"])
                    if price_info["latest_date"]:
                        all_latest.append(price_info["latest_date"])
                    if dividend_info["earliest_date"]:
                        all_earliest.append(dividend_info["earliest_date"])
                    if dividend_info["latest_date"]:
                        all_latest.append(dividend_info["latest_date"])
                
                # Add benchmark data to date range calculation
                for symbol in benchmark_stats:
                    benchmark_info = benchmark_stats[symbol]
                    if benchmark_info["earliest_date"]:
                        all_earliest.append(benchmark_info["earliest_date"])
                    if benchmark_info["latest_date"]:
                        all_latest.append(benchmark_info["latest_date"])
                
                if all_earliest and all_latest:
                    stats["date_range"]["earliest"] = min(all_earliest)
                    stats["date_range"]["latest"] = max(all_latest)
                
                # Add benchmark data to stats
                stats["benchmark_data"] = benchmark_stats
                stats["benchmark_coverage"] = benchmark_coverage_stats
        
        except sqlite3.Error as e:
            stats["error"] = f"Database error: {str(e)}"
        
        return stats
    
    def clear_all_data(self) -> bool:
        """Clear all warehouse data."""
        try:
            if not self.warehouse_db_path.exists():
                print("ℹ️  Warehouse database does not exist. Nothing to clear.")
                return True
            
            self.warehouse_service.clear_data()
            print("✅ All warehouse data cleared successfully.")
            return True
        
        except Exception as e:
            print(f"❌ Error clearing warehouse data: {str(e)}")
            return False
    
    def clear_ticker_data(self, ticker: str) -> bool:
        """Clear data for a specific ticker."""
        try:
            if not self.warehouse_db_path.exists():
                print("ℹ️  Warehouse database does not exist. Nothing to clear.")
                return True
            
            # Create a simple ticker object for the fallback case
            class SimpleTicker:
                def __init__(self, symbol):
                    self.symbol = symbol
            
            ticker_obj = SimpleTicker(ticker)
            self.warehouse_service.clear_data(ticker_obj)
            print(f"✅ Data cleared for ticker: {ticker}")
            return True
        
        except Exception as e:
            print(f"❌ Error clearing data for ticker {ticker}: {str(e)}")
            return False
    
    def clear_benchmark_data(self) -> bool:
        """Clear all benchmark data."""
        try:
            if not self.warehouse_db_path.exists():
                print("ℹ️  Warehouse database does not exist. Nothing to clear.")
                return True
            
            with sqlite3.connect(self.warehouse_db_path) as conn:
                conn.execute("DELETE FROM benchmark_data")
                conn.execute("DELETE FROM benchmark_coverage")
                conn.commit()
            
            print("✅ All benchmark data cleared successfully.")
            return True
        
        except Exception as e:
            print(f"❌ Error clearing benchmark data: {str(e)}")
            return False
    
    def backup_warehouse(self, backup_name: Optional[str] = None) -> Optional[Path]:
        """Create a backup of the warehouse database."""
        if not self.warehouse_db_path.exists():
            print("ℹ️  Warehouse database does not exist. Nothing to backup.")
            return None
        
        try:
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"warehouse_backup_{timestamp}.sqlite"
            
            backup_path = self.backup_dir / backup_name
            
            # Copy the database file
            shutil.copy2(self.warehouse_db_path, backup_path)
            
            print(f"✅ Warehouse backed up to: {backup_path}")
            return backup_path
        
        except Exception as e:
            print(f"❌ Error creating backup: {str(e)}")
            return None
    
    def restore_warehouse(self, backup_path: str) -> bool:
        """Restore warehouse from a backup."""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            # Create warehouse directory if it doesn't exist
            self.warehouse_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy backup to warehouse location
            shutil.copy2(backup_file, self.warehouse_db_path)
            
            print(f"✅ Warehouse restored from: {backup_path}")
            return True
        
        except Exception as e:
            print(f"❌ Error restoring warehouse: {str(e)}")
            return False
    
    def list_backups(self) -> List[Path]:
        """List available backup files."""
        if not self.backup_dir.exists():
            return []
        
        backup_files = list(self.backup_dir.glob("warehouse_backup_*.sqlite"))
        return sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    
    def show_statistics(self):
        """Display warehouse statistics."""
        print("📊 WAREHOUSE STATISTICS")
        print("=" * 50)
        
        stats = self.get_warehouse_statistics()
        
        if not stats["database_exists"]:
            print("ℹ️  Warehouse database does not exist.")
            return
        
        # Show relative path for better readability
        try:
            relative_path = self.warehouse_db_path.relative_to(Path.cwd())
            print(f"📁 Database Path: {relative_path}")
        except ValueError:
            # If not relative to current directory, show the path as is
            print(f"📁 Database Path: {self.warehouse_db_path}")
        print(f"💾 Database Size: {self.format_size(stats['database_size'])}")
        print(f"📈 Total Records: {stats['total_records']:,}")
        print(f"🏷️  Tickers: {len(stats['tickers'])}")
        
        if stats["tickers"]:
            print(f"   {', '.join(stats['tickers'])}")
        
        if stats.get("benchmark_symbols"):
            print(f"📊 Benchmarks: {len(stats['benchmark_symbols'])}")
            print(f"   {', '.join(stats['benchmark_symbols'])}")
        
        if stats["date_range"]["earliest"] and stats["date_range"]["latest"]:
            print(f"📅 Date Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        if stats["storage_breakdown"]:
            print("\n📊 Storage Breakdown by Ticker:")
            for ticker, data in stats["storage_breakdown"].items():
                print(f"   {ticker}: {data['total_records']:,} total records")
                print(f"      • Price: {data['price_records']:,} records ({data['price_range']})")
                print(f"      • Dividends: {data['dividend_records']:,} records ({data['dividend_range']})")
                print(f"      • Dividend Coverage: {data['dividend_coverage_periods']:,} periods ({data['dividend_coverage_range']})")
        
        if stats.get("benchmark_data"):
            print("\n📊 Benchmark Data:")
            for symbol, data in stats["benchmark_data"].items():
                print(f"   {symbol}: {data['records']:,} records ({data['earliest_date']} to {data['latest_date']})")
        
        if stats.get("benchmark_coverage"):
            print("\n📊 Benchmark Coverage:")
            for symbol, data in stats["benchmark_coverage"].items():
                print(f"   {symbol}: {data['coverage_periods']:,} coverage periods ({data['earliest_coverage']} to {data['latest_coverage']})")
        
        # Show available backups
        backups = self.list_backups()
        if backups:
            print(f"\n💾 Available Backups: {len(backups)}")
            for i, backup in enumerate(backups[:5]):  # Show last 5
                size = self.format_size(backup.stat().st_size)
                mtime = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                print(f"   {i+1}. {backup.name} ({size}, {mtime})")
            if len(backups) > 5:
                print(f"   ... and {len(backups) - 5} more")
    
    def reset_metrics(self):
        """Reset warehouse metrics (if accessible)."""
        try:
            # This would require access to the warehouse repository instance
            # For now, we'll just show a message
            print("ℹ️  Warehouse metrics are reset automatically when the application restarts.")
            print("   To reset metrics without restarting, restart the application.")
        except Exception as e:
            print(f"❌ Error resetting metrics: {str(e)}")


def main():
    """Main function for the warehouse clear script."""
    parser = argparse.ArgumentParser(
        description="Warehouse Clear Script - Administrative tool for clearing warehouse data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backend/admin/clear_warehouse.py --stats
  python backend/admin/clear_warehouse.py --clear-all
  python backend/admin/clear_warehouse.py --clear-ticker AAPL
  python backend/admin/clear_warehouse.py --clear-benchmarks
  python backend/admin/clear_warehouse.py --backup-and-clear
  python backend/admin/clear_warehouse.py --restore warehouse_backup_20241201_143022.sqlite
        """
    )
    
    parser.add_argument(
        "--stats", 
        action="store_true", 
        help="Show warehouse statistics"
    )
    
    parser.add_argument(
        "--clear-all", 
        action="store_true", 
        help="Clear all warehouse data"
    )
    
    parser.add_argument(
        "--clear-ticker", 
        type=str, 
        metavar="TICKER",
        help="Clear data for a specific ticker (e.g., AAPL)"
    )
    
    parser.add_argument(
        "--clear-benchmarks", 
        action="store_true", 
        help="Clear all benchmark data (S&P 500, etc.)"
    )
    
    parser.add_argument(
        "--backup-and-clear", 
        action="store_true", 
        help="Create backup and then clear all data"
    )
    
    parser.add_argument(
        "--backup", 
        action="store_true", 
        help="Create a backup of warehouse data"
    )
    
    parser.add_argument(
        "--restore", 
        type=str, 
        metavar="BACKUP_FILE",
        help="Restore warehouse from backup file"
    )
    
    parser.add_argument(
        "--list-backups", 
        action="store_true", 
        help="List available backup files"
    )
    
    parser.add_argument(
        "--reset-metrics", 
        action="store_true", 
        help="Reset warehouse metrics"
    )
    
    parser.add_argument(
        "--warehouse-path", 
        type=str, 
        default="../database/warehouse/warehouse.sqlite",
        help="Path to warehouse database file (default: ../database/warehouse/warehouse.sqlite)"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = WarehouseClearManager(args.warehouse_path)
    
    # Execute requested action
    if args.stats:
        manager.show_statistics()
    
    elif args.clear_all:
        print("⚠️  This will clear ALL warehouse data. This action cannot be undone.")
        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            manager.clear_all_data()
        else:
            print("❌ Operation cancelled.")
    
    elif args.clear_ticker:
        print(f"⚠️  This will clear all data for ticker: {args.clear_ticker}")
        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            manager.clear_ticker_data(args.clear_ticker)
        else:
            print("❌ Operation cancelled.")
    
    elif args.clear_benchmarks:
        print("⚠️  This will clear all benchmark data (S&P 500, etc.). This action cannot be undone.")
        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            manager.clear_benchmark_data()
        else:
            print("❌ Operation cancelled.")
    
    elif args.backup_and_clear:
        print("📦 Creating backup before clearing...")
        backup_path = manager.backup_warehouse()
        if backup_path:
            print("⚠️  This will clear ALL warehouse data. This action cannot be undone.")
            confirm = input("Are you sure? Type 'yes' to confirm: ")
            if confirm.lower() == 'yes':
                manager.clear_all_data()
            else:
                print("❌ Operation cancelled.")
    
    elif args.backup:
        manager.backup_warehouse()
    
    elif args.restore:
        manager.restore_warehouse(args.restore)
    
    elif args.list_backups:
        backups = manager.list_backups()
        if backups:
            print("💾 Available Backups:")
            for i, backup in enumerate(backups):
                size = manager.format_size(backup.stat().st_size)
                mtime = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                print(f"   {i+1}. {backup.name} ({size}, {mtime})")
        else:
            print("ℹ️  No backup files found.")
    
    elif args.reset_metrics:
        manager.reset_metrics()
    
    else:
        # No arguments provided, show help
        parser.print_help()


if __name__ == "__main__":
    main()
