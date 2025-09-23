"""
Utility for formatting tables with color codes.
Handles proper alignment when color codes are present.
"""

import re
from typing import List


class TableFormatter:
    """Utility class for formatting tables with color codes."""
    
    # ANSI escape sequence pattern
    ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
    
    @staticmethod
    def strip_ansi_codes(text: str) -> str:
        """Remove ANSI escape codes from text to get actual length."""
        return TableFormatter.ANSI_ESCAPE_PATTERN.sub('', text)
    
    @staticmethod
    def get_display_width(text: str) -> int:
        """Get the display width of text, ignoring ANSI codes."""
        return len(TableFormatter.strip_ansi_codes(text))
    
    @staticmethod
    def format_table_row(data: List[str], widths: List[int], separator: str = " | ") -> str:
        """
        Format a table row with proper alignment, accounting for color codes.
        
        Args:
            data: List of cell data (may contain color codes)
            widths: List of column widths
            separator: String to separate columns
            
        Returns:
            Formatted table row string
        """
        if len(data) != len(widths):
            raise ValueError("Data and widths lists must have the same length")
        
        formatted_cells = []
        for cell_data, width in zip(data, widths):
            # Center the content, but use actual display width for calculation
            display_width = TableFormatter.get_display_width(cell_data)
            padding = width - display_width
            left_padding = padding // 2
            right_padding = padding - left_padding
            
            formatted_cell = " " * left_padding + cell_data + " " * right_padding
            formatted_cells.append(formatted_cell)
        
        return separator.join(formatted_cells)
    
    @staticmethod
    def calculate_column_widths(data: List[List[str]], headers: List[str]) -> List[int]:
        """
        Calculate optimal column widths based on content, ignoring color codes.
        
        Args:
            data: List of rows, each row is a list of cell data
            headers: List of header strings
            
        Returns:
            List of calculated column widths
        """
        if not data:
            return [len(header) for header in headers]
        
        num_columns = len(headers)
        widths = []
        
        for col_idx in range(num_columns):
            # Start with header width
            max_width = TableFormatter.get_display_width(headers[col_idx])
            
            # Check all data rows for this column
            for row in data:
                if col_idx < len(row):
                    cell_width = TableFormatter.get_display_width(row[col_idx])
                    max_width = max(max_width, cell_width)
            
            # Add some padding
            widths.append(max_width + 2)
        
        return widths
    
    @staticmethod
    def create_table(headers: List[str], data: List[List[str]], 
                    show_borders: bool = True) -> str:
        """
        Create a formatted table with headers and data.
        
        Args:
            headers: List of header strings
            data: List of rows, each row is a list of cell data
            show_borders: Whether to show table borders
            
        Returns:
            Formatted table string
        """
        if not data:
            return ""
        
        # Calculate column widths
        widths = TableFormatter.calculate_column_widths(data, headers)
        
        # Format header
        header_line = TableFormatter.format_table_row(headers, widths)
        
        # Create separator line
        separator_line = "-" * len(TableFormatter.strip_ansi_codes(header_line))
        
        # Format data rows
        data_lines = []
        for row in data:
            data_line = TableFormatter.format_table_row(row, widths)
            data_lines.append(data_line)
        
        # Combine all parts
        table_parts = [header_line, separator_line] + data_lines
        
        return "\n".join(table_parts)
