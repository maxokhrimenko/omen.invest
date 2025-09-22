#!/usr/bin/env python3
"""
Log Rotation Script - Manages log file rotation and cleanup
Version 4.4.3 - Portfolio Analysis & Visualization

This script provides functionality to:
- Rotate log files based on size and age
- Compress old log files
- Clean up expired logs
- Maintain log directory structure
"""

import os
import sys
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import argparse


class LogRotationManager:
    """Manager for log rotation and cleanup operations."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_age_days = 30
        self.compress_after_days = 7
        self.cleanup_after_days = 30
        
    def rotate_log_file(self, file_path: Path) -> bool:
        """Rotate a single log file if it exceeds size limit."""
        if not file_path.exists():
            return False
            
        file_size = file_path.stat().st_size
        if file_size < self.max_file_size:
            return False
            
        # Create rotated filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        rotated_path = file_path.parent / rotated_name
        
        # Move current file to rotated name
        shutil.move(str(file_path), str(rotated_path))
        
        # Create new empty file
        file_path.touch()
        
        print(f"Rotated {file_path.name} -> {rotated_name} ({file_size} bytes)")
        return True
        
    def compress_old_logs(self) -> int:
        """Compress log files older than compress_after_days."""
        compressed_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.compress_after_days)
        
        for log_file in self.logs_dir.rglob("*.log"):
            if log_file.is_file():
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_mtime < cutoff_date and not log_file.name.endswith('.gz'):
                    # Compress the file
                    compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
                    
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove original file
                    log_file.unlink()
                    compressed_count += 1
                    print(f"Compressed {log_file.name} -> {compressed_file.name}")
        
        return compressed_count
        
    def cleanup_expired_logs(self) -> int:
        """Remove log files older than cleanup_after_days."""
        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_after_days)
        
        for log_file in self.logs_dir.rglob("*.log*"):
            if log_file.is_file():
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    cleaned_count += 1
                    print(f"Cleaned up {log_file.name}")
        
        return cleaned_count
        
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about current log files."""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "uncompressed_files": 0,
            "compressed_files": 0,
            "largest_file": None,
            "oldest_file": None,
            "newest_file": None
        }
        
        largest_size = 0
        oldest_time = None
        newest_time = None
        
        for log_file in self.logs_dir.rglob("*.log*"):
            if log_file.is_file():
                file_size = log_file.stat().st_size
                file_mtime = log_file.stat().st_mtime
                
                stats["total_files"] += 1
                stats["total_size"] += file_size
                
                if log_file.name.endswith('.gz'):
                    stats["compressed_files"] += 1
                else:
                    stats["uncompressed_files"] += 1
                
                if file_size > largest_size:
                    largest_size = file_size
                    stats["largest_file"] = {
                        "name": log_file.name,
                        "size": file_size,
                        "path": str(log_file)
                    }
                
                if oldest_time is None or file_mtime < oldest_time:
                    oldest_time = file_mtime
                    stats["oldest_file"] = {
                        "name": log_file.name,
                        "mtime": datetime.fromtimestamp(file_mtime),
                        "path": str(log_file)
                    }
                
                if newest_time is None or file_mtime > newest_time:
                    newest_time = file_mtime
                    stats["newest_file"] = {
                        "name": log_file.name,
                        "mtime": datetime.fromtimestamp(file_mtime),
                        "path": str(log_file)
                    }
        
        return stats
        
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def show_statistics(self):
        """Display log statistics."""
        stats = self.get_log_statistics()
        
        print("📊 LOG ROTATION STATISTICS")
        print("=" * 50)
        print(f"Total Files: {stats['total_files']}")
        print(f"Total Size: {self.format_size(stats['total_size'])}")
        print(f"Uncompressed Files: {stats['uncompressed_files']}")
        print(f"Compressed Files: {stats['compressed_files']}")
        
        if stats['largest_file']:
            print(f"Largest File: {stats['largest_file']['name']} ({self.format_size(stats['largest_file']['size'])})")
        
        if stats['oldest_file']:
            print(f"Oldest File: {stats['oldest_file']['name']} ({stats['oldest_file']['mtime']})")
        
        if stats['newest_file']:
            print(f"Newest File: {stats['newest_file']['name']} ({stats['newest_file']['mtime']})")
            
    def run_rotation(self, dry_run: bool = False) -> Dict[str, int]:
        """Run complete log rotation process."""
        results = {
            "rotated": 0,
            "compressed": 0,
            "cleaned": 0
        }
        
        print("🔄 Starting log rotation process...")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        
        # Rotate large files
        print("\n📏 Checking for large files to rotate...")
        for log_file in self.logs_dir.rglob("*.log"):
            if log_file.is_file() and not log_file.name.endswith('.gz'):
                if log_file.stat().st_size >= self.max_file_size:
                    if not dry_run:
                        if self.rotate_log_file(log_file):
                            results["rotated"] += 1
                    else:
                        print(f"Would rotate: {log_file.name} ({self.format_size(log_file.stat().st_size)})")
                        results["rotated"] += 1
        
        # Compress old files
        print(f"\n🗜️ Compressing files older than {self.compress_after_days} days...")
        if not dry_run:
            results["compressed"] = self.compress_old_logs()
        else:
            # Count files that would be compressed
            cutoff_date = datetime.now() - timedelta(days=self.compress_after_days)
            for log_file in self.logs_dir.rglob("*.log"):
                if log_file.is_file() and not log_file.name.endswith('.gz'):
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        print(f"Would compress: {log_file.name}")
                        results["compressed"] += 1
        
        # Cleanup expired files
        print(f"\n🧹 Cleaning up files older than {self.cleanup_after_days} days...")
        if not dry_run:
            results["cleaned"] = self.cleanup_expired_logs()
        else:
            # Count files that would be cleaned
            cutoff_date = datetime.now() - timedelta(days=self.cleanup_after_days)
            for log_file in self.logs_dir.rglob("*.log*"):
                if log_file.is_file():
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        print(f"Would clean up: {log_file.name}")
                        results["cleaned"] += 1
        
        return results


def main():
    """Main entry point for the log rotation script."""
    parser = argparse.ArgumentParser(
        description="Log rotation and cleanup tool for Portfolio Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backend/admin/log_rotation.py --stats                    # Show log statistics
  python backend/admin/log_rotation.py --rotate                  # Run log rotation
  python backend/admin/log_rotation.py --rotate --dry-run        # Dry run mode
  python backend/admin/log_rotation.py --compress                # Compress old logs
  python backend/admin/log_rotation.py --cleanup                 # Clean up expired logs
        """
    )
    
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Path to logs directory (default: logs)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show log statistics"
    )
    
    parser.add_argument(
        "--rotate",
        action="store_true",
        help="Run log rotation"
    )
    
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress old log files"
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up expired log files"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    parser.add_argument(
        "--max-size",
        type=int,
        default=10485760,  # 10MB
        help="Maximum file size before rotation (bytes, default: 10MB)"
    )
    
    parser.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="Maximum age before cleanup (days, default: 30)"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = LogRotationManager(args.logs_dir)
    manager.max_file_size = args.max_size
    manager.cleanup_after_days = args.max_age
    
    # Check if logs directory exists
    if not manager.logs_dir.exists():
        print(f"❌ Logs directory not found: {manager.logs_dir}")
        print("ℹ️  Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Execute requested actions
    if args.stats:
        manager.show_statistics()
    elif args.rotate:
        results = manager.run_rotation(dry_run=args.dry_run)
        print(f"\n✅ Rotation complete: {results['rotated']} rotated, {results['compressed']} compressed, {results['cleaned']} cleaned")
    elif args.compress:
        if args.dry_run:
            print("🔍 DRY RUN MODE - No files will be compressed")
        compressed = manager.compress_old_logs()
        print(f"✅ Compressed {compressed} files")
    elif args.cleanup:
        if args.dry_run:
            print("🔍 DRY RUN MODE - No files will be cleaned")
        cleaned = manager.cleanup_expired_logs()
        print(f"✅ Cleaned up {cleaned} files")
    else:
        # Default action: show statistics
        manager.show_statistics()
        print("\n💡 Use --help to see all available options.")


if __name__ == "__main__":
    main()
