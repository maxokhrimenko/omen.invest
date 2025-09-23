#!/usr/bin/env python3
"""
Logs Clear Script - Administrative tool for clearing application logs.
Version 4.4.3 - Portfolio Analysis & Visualization

This script provides functionality to:
- Clear all logs (frontend, backend, CLI, total)

Usage:
    python backend/admin/logs_clear.py --clear-all
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
        self.frontend_dir = self.logs_dir / "frontend"
        self.backend_dir = self.logs_dir / "backend"
        self.cli_dir = self.logs_dir / "CLI"
        self.total_dir = self.logs_dir / "total"
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about current logs."""
        stats = {
            "frontend": {
                "count": 0,
                "total_size": 0,
                "files": []
            },
            "backend": {
                "count": 0,
                "total_size": 0,
                "files": []
            },
            "CLI": {
                "count": 0,
                "total_size": 0,
                "files": []
            },
            "total": {
                "count": 0,
                "total_size": 0,
                "files": []
            }
        }
        
        # Count frontend logs
        if self.frontend_dir.exists():
            for file_path in self.frontend_dir.glob("*.log"):
                file_size = file_path.stat().st_size
                stats["frontend"]["count"] += 1
                stats["frontend"]["total_size"] += file_size
                stats["frontend"]["files"].append({
                    "name": file_path.name,
                    "size": file_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
        
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
        
        # Count CLI logs
        if self.cli_dir.exists():
            for file_path in self.cli_dir.glob("*.log"):
                file_size = file_path.stat().st_size
                stats["CLI"]["count"] += 1
                stats["CLI"]["total_size"] += file_size
                stats["CLI"]["files"].append({
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
        
        print(f"\n📁 Frontend Logs (API/Portfolio):")
        print(f"   Count: {stats['frontend']['count']} files")
        print(f"   Total Size: {self.format_size(stats['frontend']['total_size'])}")
        
        if stats['frontend']['files']:
            print("   Recent Files:")
            for file_info in sorted(stats['frontend']['files'], 
                                  key=lambda x: x['modified'], reverse=True)[:5]:
                print(f"     {file_info['name']} ({self.format_size(file_info['size'])}) - {file_info['modified']}")
        
        print(f"\n📁 Backend Logs (API/Portfolio):")
        print(f"   Count: {stats['backend']['count']} files")
        print(f"   Total Size: {self.format_size(stats['backend']['total_size'])}")
        
        if stats['backend']['files']:
            print("   Recent Files:")
            for file_info in sorted(stats['backend']['files'], 
                                  key=lambda x: x['modified'], reverse=True)[:5]:
                print(f"     {file_info['name']} ({self.format_size(file_info['size'])}) - {file_info['modified']}")
        
        print(f"\n📁 CLI Logs (Command Line):")
        print(f"   Count: {stats['CLI']['count']} files")
        print(f"   Total Size: {self.format_size(stats['CLI']['total_size'])}")
        
        if stats['CLI']['files']:
            print("   Recent Files:")
            for file_info in sorted(stats['CLI']['files'], 
                                  key=lambda x: x['modified'], reverse=True)[:5]:
                print(f"     {file_info['name']} ({self.format_size(file_info['size'])}) - {file_info['modified']}")
        
        print(f"\n📁 Total Logs (All Components):")
        print(f"   Count: {stats['total']['count']} files")
        print(f"   Total Size: {self.format_size(stats['total']['total_size'])}")
        
        if stats['total']['files']:
            print("   Files:")
            for file_info in stats['total']['files']:
                print(f"     {file_info['name']} ({self.format_size(file_info['size'])}) - {file_info['modified']}")
        
        total_size = stats['frontend']['total_size'] + stats['backend']['total_size'] + stats['CLI']['total_size'] + stats['total']['total_size']
        print(f"\n💾 Total Storage Used: {self.format_size(total_size)}")
    
    def clear_directory(self, directory: Path, name: str) -> bool:
        """Clear all log files in a directory."""
        if not directory.exists():
            print(f"ℹ️  No {name} logs to clear.")
            return True
        
        try:
            # Count files before deletion
            file_count = len(list(directory.glob("*.log")))
            
            # Remove all log files
            for file_path in directory.glob("*.log"):
                file_path.unlink()
            
            if file_count > 0:
                print(f"✅ Cleared {file_count} {name} log files.")
            else:
                print(f"ℹ️  No {name} log files found to clear.")
            
            return True
        except Exception as e:
            print(f"❌ Error clearing {name} logs: {e}")
            return False
    
    def clear_all(self, confirm: bool = True) -> bool:
        """Clear all logs (frontend, backend, CLI, and total)."""
        if confirm:
            response = input("⚠️  This will delete ALL logs (frontend, backend, CLI, and total). Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return False
        
        success = True
        success &= self.clear_directory(self.frontend_dir, "frontend")
        success &= self.clear_directory(self.backend_dir, "backend")
        success &= self.clear_directory(self.cli_dir, "CLI")
        success &= self.clear_directory(self.total_dir, "total")
        
        if success:
            print("✅ All logs cleared successfully.")
        else:
            print("❌ Some errors occurred while clearing logs.")
        
        return success


def main():
    """Main entry point for the logs clear script."""
    parser = argparse.ArgumentParser(
        description="Administrative tool for clearing Portfolio Analysis Tool logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backend/admin/logs_clear.py --clear-all               # Clear all logs
        """
    )
    
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Path to logs directory (default: logs)"
    )
    
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all logs (frontend, backend, CLI, and total)"
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
    if args.clear_all:
        manager.clear_all(confirm=not args.force)
    else:
        # Default action: show statistics
        manager.show_statistics()
        print("\n💡 Use --clear-all to clear all logs.")


if __name__ == "__main__":
    main()
