#!/usr/bin/env python3
"""
Log Search Utility - Search and filter log files
Version 4.3.0 - Advanced Portfolio Analysis & Visualization

This script provides functionality to:
- Search logs by text, log level, or log ID
- Filter by date range
- Show context around matches
- Export search results
"""

import os
import sys
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


class LogSearchManager:
    """Manager for log search operations."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        
    def search_logs(self, 
                   query: str = None,
                   log_level: str = None,
                   log_id: str = None,
                   start_date: str = None,
                   end_date: str = None,
                   context_lines: int = 0) -> List[Dict[str, Any]]:
        """Search log files with various filters."""
        results = []
        
        # Parse date filters
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                print(f"Invalid start date format: {start_date}. Use YYYY-MM-DD")
                return results
                
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                print(f"Invalid end date format: {end_date}. Use YYYY-MM-DD")
                return results
        
        # Search all log files
        for log_file in self.logs_dir.rglob("*.log*"):
            if not log_file.is_file():
                continue
                
            try:
                # Handle compressed files
                if log_file.name.endswith('.gz'):
                    import gzip
                    with gzip.open(log_file, 'rt', encoding='utf-8') as f:
                        lines = f.readlines()
                else:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                
                # Search through lines
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse log line to extract timestamp and level
                    log_entry = self._parse_log_line(line)
                    if not log_entry:
                        continue
                    
                    # Apply filters
                    if not self._matches_filters(log_entry, query, log_level, log_id, start_dt, end_dt):
                        continue
                    
                    # Add context lines if requested
                    context = []
                    if context_lines > 0:
                        start_idx = max(0, line_num - context_lines - 1)
                        end_idx = min(len(lines), line_num + context_lines)
                        context = [lines[i].strip() for i in range(start_idx, end_idx) if i != line_num - 1]
                    
                    results.append({
                        'file': str(log_file.relative_to(self.logs_dir)),
                        'line_number': line_num,
                        'timestamp': log_entry['timestamp'],
                        'level': log_entry['level'],
                        'logger': log_entry['logger'],
                        'message': log_entry['message'],
                        'log_id': log_entry.get('log_id'),
                        'context': context,
                        'full_line': line
                    })
                    
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
                continue
        
        return results
    
    def _parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a log line to extract structured information."""
        # Pattern for standard log format
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+)\s+\| ([^|]+) \| ([^|]+) \| (.*)'
        match = re.match(pattern, line)
        
        if not match:
            return None
            
        timestamp_str, level, logger, func_info, message = match.groups()
        
        # Extract log ID if present
        log_id = None
        if 'LOG_ID:' in message:
            id_match = re.search(r'LOG_ID:(\w+)', message)
            if id_match:
                log_id = id_match.group(1)
                # Remove log ID from message for cleaner display
                message = re.sub(r' \| LOG_ID:\w+', '', message)
        
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            timestamp = None
        
        return {
            'timestamp': timestamp,
            'level': level,
            'logger': logger.strip(),
            'message': message.strip(),
            'log_id': log_id
        }
    
    def _matches_filters(self, log_entry: Dict[str, Any], 
                        query: str, log_level: str, log_id: str,
                        start_dt: datetime, end_dt: datetime) -> bool:
        """Check if log entry matches all specified filters."""
        
        # Text query filter
        if query:
            if not re.search(query, log_entry['message'], re.IGNORECASE):
                return False
        
        # Log level filter
        if log_level:
            if log_entry['level'].upper() != log_level.upper():
                return False
        
        # Log ID filter
        if log_id:
            if not log_entry.get('log_id') or log_id not in log_entry['log_id']:
                return False
        
        # Date range filter
        if start_dt and log_entry['timestamp']:
            if log_entry['timestamp'] < start_dt:
                return False
                
        if end_dt and log_entry['timestamp']:
            if log_entry['timestamp'] > end_dt:
                return False
        
        return True
    
    def format_results(self, results: List[Dict[str, Any]], show_context: bool = False) -> str:
        """Format search results for display."""
        if not results:
            return "No matching log entries found."
        
        output = []
        output.append(f"Found {len(results)} matching log entries:")
        output.append("=" * 80)
        
        for result in results:
            # Main log entry
            output.append(f"📁 {result['file']}:{result['line_number']}")
            output.append(f"🕐 {result['timestamp']} | {result['level']} | {result['logger']}")
            if result['log_id']:
                output.append(f"🆔 ID: {result['log_id']}")
            output.append(f"💬 {result['message']}")
            
            # Context lines
            if show_context and result['context']:
                output.append("📝 Context:")
                for ctx_line in result['context']:
                    output.append(f"   {ctx_line}")
            
            output.append("-" * 80)
        
        return "\n".join(output)
    
    def export_results(self, results: List[Dict[str, Any]], output_file: str):
        """Export search results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.format_results(results, show_context=True))
        print(f"Results exported to {output_file}")


def main():
    """Main entry point for the log search script."""
    parser = argparse.ArgumentParser(
        description="Search and filter log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backend/admin/log_search.py --query "error"                    # Search for "error"
  python backend/admin/log_search.py --level ERROR                     # Search for ERROR level
  python backend/admin/log_search.py --log-id abc123                   # Search by log ID
  python backend/admin/log_search.py --start-date 2024-01-01           # Search from date
  python backend/admin/log_search.py --query "portfolio" --context 3   # Search with context
  python backend/admin/log_search.py --export results.txt              # Export results
        """
    )
    
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Path to logs directory (default: logs)"
    )
    
    parser.add_argument(
        "--query", "-q",
        help="Text to search for in log messages"
    )
    
    parser.add_argument(
        "--level", "-l",
        help="Log level to filter by (DEBUG, INFO, WARN, ERROR, CRITICAL)"
    )
    
    parser.add_argument(
        "--log-id", "-i",
        help="Log ID to search for"
    )
    
    parser.add_argument(
        "--start-date", "-s",
        help="Start date for filtering (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end-date", "-e",
        help="End date for filtering (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--context", "-c",
        type=int,
        default=0,
        help="Number of context lines to show around matches"
    )
    
    parser.add_argument(
        "--export", "-o",
        help="Export results to file"
    )
    
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=100,
        help="Maximum number of results to show (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = LogSearchManager(args.logs_dir)
    
    # Check if logs directory exists
    if not manager.logs_dir.exists():
        print(f"❌ Logs directory not found: {manager.logs_dir}")
        print("ℹ️  Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Perform search
    results = manager.search_logs(
        query=args.query,
        log_level=args.level,
        log_id=args.log_id,
        start_date=args.start_date,
        end_date=args.end_date,
        context_lines=args.context
    )
    
    # Limit results
    if len(results) > args.limit:
        results = results[:args.limit]
        print(f"⚠️  Showing first {args.limit} results (total: {len(results)})")
    
    # Display or export results
    if args.export:
        manager.export_results(results, args.export)
    else:
        print(manager.format_results(results, show_context=args.context > 0))


if __name__ == "__main__":
    main()
