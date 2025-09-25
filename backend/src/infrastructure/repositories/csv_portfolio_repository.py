import pandas as pd
import os
from typing import List
from ...application.interfaces.repositories import PortfolioRepository
from ...domain.entities.portfolio import Portfolio
from ...domain.entities.position import Position
from ...domain.entities.ticker import Ticker

class CsvPortfolioRepository(PortfolioRepository):
    def __init__(self):
        pass
    
    def load(self, file_path: str) -> Portfolio:
        """Load portfolio from CSV file."""
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Portfolio file not found: {file_path}")
            
            df = pd.read_csv(file_path)
            
            self._validate_csv_format(df)
            
            positions = []
            for idx, row in df.iterrows():
                # Convert ticker symbol format (e.g., BRK.B -> BRK-B for Yahoo Finance)
                ticker_symbol = str(row['ticker']).replace('.', '-')
                ticker = Ticker(ticker_symbol)
                position = Position(ticker, float(row['position']))
                positions.append(position)
            
            if not positions:
                raise ValueError("No valid positions found in CSV file")
            
            return Portfolio(positions)
            
        except Exception as e:
            raise ValueError(f"Error loading portfolio from CSV: {str(e)}")
    
    def _validate_csv_format(self, df: pd.DataFrame) -> None:
        """Validate that CSV has required columns and format."""
        
        required_columns = ['ticker', 'position']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        if df.empty:
            raise ValueError("CSV file is empty")
        
        # Check for valid data types
        for idx, row in df.iterrows():
            if pd.isna(row['ticker']) or str(row['ticker']).strip() == '':
                raise ValueError(f"Empty ticker symbol at row {idx + 1}")
            
            try:
                position_value = float(row['position'])
                if position_value <= 0:
                    raise ValueError(f"Invalid position value at row {idx + 1}: {position_value}")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid position value at row {idx + 1}: {row['position']}")
    
    def save(self, portfolio: Portfolio, file_path: str) -> None:
        """Save portfolio to CSV file."""
        
        try:
            data = []
            for position in portfolio.get_positions():
                # Convert ticker symbol back to original format (e.g., BRK-B -> BRK.B)
                ticker_symbol = position.ticker.symbol.replace('-', '.')
                data.append({
                    'ticker': ticker_symbol,
                    'position': float(position.quantity)
                })
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
        except Exception as e:
            raise ValueError(f"Error saving portfolio to CSV: {str(e)}")
