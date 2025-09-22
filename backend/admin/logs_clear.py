#!/usr/bin/env python3
"""
Logs Clear Script - Administrative tool for clearing application logs.
Version 4.4.3 - Portfolio Analysis & Visualization

This script provides functionality to:
- Clear all backend logs (CLI)
- Clear all frontend logs (API/Portfolio sessions)
- Clear all total logs
- Show log statistics including frontend portfolio sessions
- Backup logs before clearing (optional)

Usage:
    python backend/admin/logs_clear.py --help
    python backend/admin/logs_clear.py --clear-all
    python backend/admin/logs_clear.py --clear-backend
    python backend/admin/logs_clear.py --clear-frontend
    python backend/admin/logs_clear.py --clear-total
    python backend/admin/logs_clear.py --stats
    python backend/admin/logs_clear.py --backup-and-clear
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
        self.backend_dir = self.logs_dir / "backend"
        self.frontend_dir = self.logs_dir / "frontend"
        self.total_dir = self.logs_dir / "total"
        self.backup_dir = self.logs_dir / "backups"
        
        # Legacy backend/logs/ directory support removed - all logs now go to project root logs/
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about current logs."""
        stats = {
            "backend": {
                "count": 0,
                "total_size": 0,
                "files": []
            },
            "frontend": {
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
        
        # Count backend logs
        if self.backend_dir.exists():
            for file_path in self.backend_dir.glob("*.log"):
                file_size = file_path.stat().st_size
                stats["backend"]["count"] += 1
                stats["backend"]["total_size"] += file_size
                stats["backend"]["files"].append({
                    "name": file_path.name,
                    "size": file_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
        
        # Count frontend logs (only check project root logs/frontend)
        if self.frontend_dir.exists():
            for file_path in self.frontend_dir.glob("*.log"):
                file_size = file_path.stat().st_size
                stats["frontend"]["count"] += 1
                stats["frontend"]["total_size"] += file_size
                stats["frontend"]["files"].append({
                    "name": file_path.name,
                    "size": file_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "location": str(self.frontend_dir)
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
        
        print(f"\n📁 Backend Logs (CLI):")
        print(f"   Count: {stats['backend']['count']} files")
        print(f"   Total Size: {self.format_size(stats['backend']['total_size'])}")
        
        if stats['backend']['files']:
            print("   Recent Files:")
            for file_info in sorted(stats['backend']['files'], 
                                  key=lambda x: x['modified'], reverse=True)[:5]:
                print(f"     {file_info['name']} ({self.format_size(file_info['size'])}) - {file_info['modified']}")
        
        print(f"\n📁 Frontend Logs (API):")
        print(f"   Count: {stats['frontend']['count']} files")
        print(f"   Total Size: {self.format_size(stats['frontend']['total_size'])}")
        
        if stats['frontend']['files']:
            print("   Recent Files:")
            for file_info in sorted(stats['frontend']['files'], 
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
        
        total_size = stats['backend']['total_size'] + stats['frontend']['total_size'] + stats['total']['total_size'] + stats['backups']['total_size']
        print(f"\n💾 Total Storage Used: {self.format_size(total_size)}")
    
    def create_backup(self) -> str:
        """Create a backup of all current logs."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"logs_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy backend logs
        if self.backend_dir.exists():
            backend_backup = backup_path / "backend"
            shutil.copytree(self.backend_dir, backend_backup)
        
        # Copy frontend logs (only project root logs/frontend)
        if self.frontend_dir.exists():
            frontend_backup = backup_path / "frontend"
            shutil.copytree(self.frontend_dir, frontend_backup)
        
        # Copy total logs
        if self.total_dir.exists():
            total_backup = backup_path / "total"
            shutil.copytree(self.total_dir, total_backup)
        
        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)
    
    def clear_backend(self, confirm: bool = True) -> bool:
        """Clear all backend logs."""
        if not self.backend_dir.exists():
            print("ℹ️  No backend logs to clear.")
            return True
        
        if confirm:
            response = input(f"⚠️  This will delete all backend logs in {self.backend_dir}. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        try:
            # Count files before deletion
            file_count = len(list(self.backend_dir.glob("*.log")))
            
            # Remove all log files
            for file_path in self.backend_dir.glob("*.log"):
                file_path.unlink()
            
            print(f"✅ Cleared {file_count} backend log files.")
            return True
        except Exception as e:
            print(f"❌ Error clearing backend logs: {e}")
            return False
    
    def clear_frontend(self, confirm: bool = True) -> bool:
        """Clear all frontend logs."""
        if not self.frontend_dir.exists():
            print("ℹ️  No frontend logs to clear.")
            return True
        
        if confirm:
            response = input(f"⚠️  This will delete all frontend logs in {self.frontend_dir}. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        try:
            # Count files before deletion
            file_count = len(list(self.frontend_dir.glob("*.log")))
            
            # Remove all log files
            for file_path in self.frontend_dir.glob("*.log"):
                file_path.unlink()
            
            if file_count == 0:
                print("ℹ️  No frontend log files found to clear.")
            else:
                print(f"✅ Cleared {file_count} frontend log files from {self.frontend_dir}")
            
            return True
        except Exception as e:
            print(f"❌ Error clearing frontend logs: {e}")
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
        """Clear all logs (backend, frontend, and total)."""
        if confirm:
            response = input("⚠️  This will delete ALL logs (backend, frontend, and total). Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        success = True
        success &= self.clear_backend(confirm=False)
        success &= self.clear_frontend(confirm=False)
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
  python backend/admin/logs_clear.py --stats                    # Show log statistics
  python backend/admin/logs_clear.py --clear-backend           # Clear backend logs (CLI)
  python backend/admin/logs_clear.py --clear-frontend          # Clear frontend logs (API)
  python backend/admin/logs_clear.py --clear-total             # Clear total logs
  python backend/admin/logs_clear.py --clear-all               # Clear all logs
  python backend/admin/logs_clear.py --backup-and-clear        # Backup and clear all logs
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
        "--clear-backend",
        action="store_true",
        help="Clear all backend logs (CLI)"
    )
    
    parser.add_argument(
        "--clear-frontend",
        action="store_true",
        help="Clear all frontend logs (API)"
    )
    
    parser.add_argument(
        "--clear-total",
        action="store_true",
        help="Clear all total logs"
    )
    
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all logs (backend, frontend, and total)"
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
    elif args.clear_backend:
        manager.clear_backend(confirm=not args.force)
    elif args.clear_frontend:
        manager.clear_frontend(confirm=not args.force)
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
