import pandas as pd
import os
from typing import List
from ...application.interfaces.repositories import PortfolioRepository
from ...domain.entities.portfolio import Portfolio
from ...domain.entities.position import Position
from ...domain.entities.ticker import Ticker
from ..logging.logger_service import get_logger_service
from ..logging.decorators import log_file_operation

class CsvPortfolioRepository(PortfolioRepository):
    def __init__(self):
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("infrastructure")
    
    @log_file_operation("load_csv", include_path=True)
    def load(self, file_path: str) -> Portfolio:
        """Load portfolio from CSV file."""
        self._logger.info(f"Loading portfolio from CSV: {file_path}")
        
        try:
            if not os.path.exists(file_path):
                self._logger.error(f"Portfolio file not found: {file_path}")
                raise FileNotFoundError(f"Portfolio file not found: {file_path}")
            
            self._logger.debug("Reading CSV file with pandas")
            df = pd.read_csv(file_path)
            self._logger.debug(f"CSV file loaded: {len(df)} rows, {len(df.columns)} columns")
            
            self._validate_csv_format(df)
            
            positions = []
            for idx, row in df.iterrows():
                # Convert ticker symbol format (e.g., BRK.B -> BRK-B for Yahoo Finance)
                ticker_symbol = str(row['ticker']).replace('.', '-')
                ticker = Ticker(ticker_symbol)
                position = Position(ticker, float(row['position']))
                positions.append(position)
                self._logger.debug(f"Created position {idx + 1}: {ticker_symbol} x {row['position']}")
            
            if not positions:
                self._logger.error("No valid positions found in CSV file")
                raise ValueError("No valid positions found in CSV file")
            
            self._logger.info(f"Successfully loaded {len(positions)} positions from CSV")
            self._logger_service.log_file_operation("load_csv", file_path, True, {"positions_count": len(positions)})
            
            return Portfolio(positions)
            
        except Exception as e:
            self._logger.error(f"Error loading portfolio from CSV: {str(e)}")
            self._logger_service.log_file_operation("load_csv", file_path, False, {"error": str(e)})
            raise ValueError(f"Error loading portfolio from CSV: {str(e)}")
    
    def _validate_csv_format(self, df: pd.DataFrame) -> None:
        """Validate that CSV has required columns and format."""
        self._logger.debug("Validating CSV format")
        
        required_columns = ['ticker', 'position']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self._logger.error(f"CSV validation failed: missing columns {missing_columns}")
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        if df.empty:
            self._logger.error("CSV validation failed: empty file")
            raise ValueError("CSV file is empty")
        
        self._logger.debug(f"CSV validation: {len(df)} rows to validate")
        
        # Check for valid data types
        for idx, row in df.iterrows():
            if pd.isna(row['ticker']) or str(row['ticker']).strip() == '':
                self._logger.error(f"CSV validation failed: empty ticker at row {idx + 1}")
                raise ValueError(f"Empty ticker symbol at row {idx + 1}")
            
            try:
                position_value = float(row['position'])
                if position_value <= 0:
                    self._logger.error(f"CSV validation failed: invalid position at row {idx + 1}: {position_value}")
                    raise ValueError(f"Invalid position value at row {idx + 1}: {position_value}")
            except (ValueError, TypeError):
                self._logger.error(f"CSV validation failed: position conversion error at row {idx + 1}: {row['position']}")
                raise ValueError(f"Invalid position value at row {idx + 1}: {row['position']}")
        
        self._logger.debug("CSV validation successful")
    
    @log_file_operation("save_csv", include_path=True)
    def save(self, portfolio: Portfolio, file_path: str) -> None:
        """Save portfolio to CSV file."""
        self._logger.info(f"Saving portfolio to CSV: {file_path}")
        
        try:
            data = []
            for position in portfolio.get_positions():
                # Convert ticker symbol back to original format (e.g., BRK-B -> BRK.B)
                ticker_symbol = position.ticker.symbol.replace('-', '.')
                data.append({
                    'ticker': ticker_symbol,
                    'position': float(position.quantity)
                })
                self._logger.debug(f"Prepared position for saving: {ticker_symbol} x {position.quantity}")
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
            self._logger.info(f"Successfully saved {len(data)} positions to CSV")
            self._logger_service.log_file_operation("save_csv", file_path, True, {"positions_count": len(data)})
            
        except Exception as e:
            self._logger.error(f"Error saving portfolio to CSV: {str(e)}")
            self._logger_service.log_file_operation("save_csv", file_path, False, {"error": str(e)})
            raise ValueError(f"Error saving portfolio to CSV: {str(e)}")
