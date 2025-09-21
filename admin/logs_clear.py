#!/usr/bin/env python3
"""
Logs Clear Script - Administrative tool for clearing application logs.

This script provides functionality to:
- Clear all session logs
- Clear all total logs
- Clear specific session logs
- Show log statistics
- Backup logs before clearing (optional)

Usage:
    python admin/logs_clear.py --help
    python admin/logs_clear.py --clear-all
    python admin/logs_clear.py --clear-sessions
    python admin/logs_clear.py --clear-total
    python admin/logs_clear.py --stats
    python admin/logs_clear.py --backup-and-clear
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class LogsClearManager:
    """Manager for clearing and managing application logs."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.sessions_dir = self.logs_dir / "sessions"
        self.total_dir = self.logs_dir / "total"
        self.backup_dir = self.logs_dir / "backups"
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about current logs."""
        stats = {
            "sessions": {
                "count": 0,
                "total_size": 0,
                "files": []
            },
            "total": {
                "count": 0,
                "total_size": 0,
                "files": []
            },
            "backups": {
                "count": 0,
                "total_size": 0,
                "files": []
            }
        }
        
        # Count session logs
        if self.sessions_dir.exists():
            for file_path in self.sessions_dir.glob("*.log"):
                file_size = file_path.stat().st_size
                stats["sessions"]["count"] += 1
                stats["sessions"]["total_size"] += file_size
                stats["sessions"]["files"].append({
                    "name": file_path.name,
                    "size": file_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
        
        # Count total logs
        if self.total_dir.exists():
            for file_path in self.total_dir.glob("*.log"):
                file_size = file_path.stat().st_size
                stats["total"]["count"] += 1
                stats["total"]["total_size"] += file_size
                stats["total"]["files"].append({
                    "name": file_path.name,
                    "size": file_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
        
        # Count backup logs
        if self.backup_dir.exists():
            for file_path in self.backup_dir.glob("*.log"):
                file_size = file_path.stat().st_size
                stats["backups"]["count"] += 1
                stats["backups"]["total_size"] += file_size
                stats["backups"]["files"].append({
                    "name": file_path.name,
                    "size": file_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
        
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
        
        print("📊 LOG STATISTICS")
        print("=" * 50)
        
        print(f"\n📁 Session Logs:")
        print(f"   Count: {stats['sessions']['count']} files")
        print(f"   Total Size: {self.format_size(stats['sessions']['total_size'])}")
        
        if stats['sessions']['files']:
            print("   Recent Files:")
            for file_info in sorted(stats['sessions']['files'], 
                                  key=lambda x: x['modified'], reverse=True)[:5]:
                print(f"     {file_info['name']} ({self.format_size(file_info['size'])}) - {file_info['modified']}")
        
        print(f"\n📁 Total Logs:")
        print(f"   Count: {stats['total']['count']} files")
        print(f"   Total Size: {self.format_size(stats['total']['total_size'])}")
        
        if stats['total']['files']:
            print("   Files:")
            for file_info in stats['total']['files']:
                print(f"     {file_info['name']} ({self.format_size(file_info['size'])}) - {file_info['modified']}")
        
        print(f"\n📁 Backup Logs:")
        print(f"   Count: {stats['backups']['count']} files")
        print(f"   Total Size: {self.format_size(stats['backups']['total_size'])}")
        
        total_size = stats['sessions']['total_size'] + stats['total']['total_size'] + stats['backups']['total_size']
        print(f"\n💾 Total Storage Used: {self.format_size(total_size)}")
    
    def create_backup(self) -> str:
        """Create a backup of all current logs."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"logs_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy session logs
        if self.sessions_dir.exists():
            sessions_backup = backup_path / "sessions"
            shutil.copytree(self.sessions_dir, sessions_backup)
        
        # Copy total logs
        if self.total_dir.exists():
            total_backup = backup_path / "total"
            shutil.copytree(self.total_dir, total_backup)
        
        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)
    
    def clear_sessions(self, confirm: bool = True) -> bool:
        """Clear all session logs."""
        if not self.sessions_dir.exists():
            print("ℹ️  No session logs to clear.")
            return True
        
        if confirm:
            response = input(f"⚠️  This will delete all session logs in {self.sessions_dir}. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        try:
            # Count files before deletion
            file_count = len(list(self.sessions_dir.glob("*.log")))
            
            # Remove all log files
            for file_path in self.sessions_dir.glob("*.log"):
                file_path.unlink()
            
            print(f"✅ Cleared {file_count} session log files.")
            return True
        except Exception as e:
            print(f"❌ Error clearing session logs: {e}")
            return False
    
    def clear_total(self, confirm: bool = True) -> bool:
        """Clear all total logs."""
        if not self.total_dir.exists():
            print("ℹ️  No total logs to clear.")
            return True
        
        if confirm:
            response = input(f"⚠️  This will delete all total logs in {self.total_dir}. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        try:
            # Count files before deletion
            file_count = len(list(self.total_dir.glob("*.log")))
            
            # Remove all log files
            for file_path in self.total_dir.glob("*.log"):
                file_path.unlink()
            
            print(f"✅ Cleared {file_count} total log files.")
            return True
        except Exception as e:
            print(f"❌ Error clearing total logs: {e}")
            return False
    
    def clear_all(self, confirm: bool = True) -> bool:
        """Clear all logs (sessions and total)."""
        if confirm:
            response = input("⚠️  This will delete ALL logs (sessions and total). Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        success = True
        success &= self.clear_sessions(confirm=False)
        success &= self.clear_total(confirm=False)
        
        if success:
            print("✅ All logs cleared successfully.")
        else:
            print("❌ Some errors occurred while clearing logs.")
        
        return success
    
    def backup_and_clear(self, confirm: bool = True) -> bool:
        """Create backup and clear all logs."""
        if confirm:
            response = input("⚠️  This will backup and then delete ALL logs. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        try:
            # Create backup
            backup_path = self.create_backup()
            
            # Clear all logs
            success = self.clear_all(confirm=False)
            
            if success:
                print(f"✅ Backup created and all logs cleared. Backup location: {backup_path}")
            else:
                print("❌ Backup created but some errors occurred while clearing logs.")
            
            return success
        except Exception as e:
            print(f"❌ Error during backup and clear: {e}")
            return False


def main():
    """Main entry point for the logs clear script."""
    parser = argparse.ArgumentParser(
        description="Administrative tool for managing Portfolio Analysis Tool logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python admin/logs_clear.py --stats                    # Show log statistics
  python admin/logs_clear.py --clear-sessions          # Clear session logs
  python admin/logs_clear.py --clear-total             # Clear total logs
  python admin/logs_clear.py --clear-all               # Clear all logs
  python admin/logs_clear.py --backup-and-clear        # Backup and clear all logs
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
        "--clear-sessions",
        action="store_true",
        help="Clear all session logs"
    )
    
    parser.add_argument(
        "--clear-total",
        action="store_true",
        help="Clear all total logs"
    )
    
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all logs (sessions and total)"
    )
    
    parser.add_argument(
        "--backup-and-clear",
        action="store_true",
        help="Create backup and clear all logs"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = LogsClearManager(args.logs_dir)
    
    # Check if logs directory exists
    if not manager.logs_dir.exists():
        print(f"❌ Logs directory not found: {manager.logs_dir}")
        print("ℹ️  Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Execute requested action
    if args.stats:
        manager.show_statistics()
    elif args.clear_sessions:
        manager.clear_sessions(confirm=not args.force)
    elif args.clear_total:
        manager.clear_total(confirm=not args.force)
    elif args.clear_all:
        manager.clear_all(confirm=not args.force)
    elif args.backup_and_clear:
        manager.backup_and_clear(confirm=not args.force)
    else:
        # Default action: show statistics
        manager.show_statistics()
        print("\n💡 Use --help to see all available options.")


if __name__ == "__main__":
    main()
