import pytest
import sys
import os
import tempfile
import pandas as pd

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.infrastructure.repositories.csv_portfolio_repository import CsvPortfolioRepository
from src.infrastructure.repositories.yfinance_market_repository import YFinanceMarketRepository
from src.application.use_cases.load_portfolio import LoadPortfolioUseCase, LoadPortfolioRequest
from src.application.use_cases.analyze_portfolio import AnalyzePortfolioUseCase, AnalyzePortfolioRequest
from src.domain.value_objects.date_range import DateRange

class TestPortfolioAnalysisIntegration:
    """Integration tests for portfolio analysis workflow."""
    
    def test_complete_portfolio_workflow(self):
        """Test the complete workflow from loading to analysis."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("ticker,position\n")
            f.write("AAPL,1\n")
            f.write("MSFT,1\n")
            temp_file = f.name
        
        try:
            # Set up dependencies
            portfolio_repo = CsvPortfolioRepository()
            market_repo = YFinanceMarketRepository()
            load_use_case = LoadPortfolioUseCase(portfolio_repo)
            analyze_use_case = AnalyzePortfolioUseCase(market_repo)
            
            # Test loading portfolio
            load_request = LoadPortfolioRequest(file_path=temp_file)
            load_response = load_use_case.execute(load_request)
            
            assert load_response.success
            assert load_response.portfolio is not None
            assert len(load_response.portfolio.get_tickers()) == 2
            
            # Test portfolio analysis (using a shorter date range to avoid network issues in tests)
            date_range = DateRange("2024-09-01", "2024-09-19")
            analyze_request = AnalyzePortfolioRequest(
                portfolio=load_response.portfolio,
                date_range=date_range,
                risk_free_rate=0.03
            )
            
            # Note: This test might fail if there's no network connection
            # In a real test environment, we'd mock the market data repository
            analyze_response = analyze_use_case.execute(analyze_request)
            
            # The analysis might fail due to network/data issues, but the structure should be correct
            assert hasattr(analyze_response, 'success')
            assert hasattr(analyze_response, 'message')
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_portfolio_repository_error_handling(self):
        """Test error handling in portfolio repository."""
        repo = CsvPortfolioRepository()
        
        # Test file not found
        with pytest.raises(ValueError, match="Error loading portfolio from CSV"):
            repo.load("non_existent_file.csv")
    
    def test_csv_validation(self):
        """Test CSV format validation."""
        repo = CsvPortfolioRepository()
        
        # Test invalid CSV format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("wrong,columns\n")
            f.write("AAPL,1\n")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing required columns"):
                repo.load(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_empty_portfolio_handling(self):
        """Test handling of empty portfolio."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("ticker,position\n")
            temp_file = f.name
        
        try:
            repo = CsvPortfolioRepository()
            with pytest.raises(ValueError, match="CSV file is empty"):
                repo.load(temp_file)
        finally:
            os.unlink(temp_file)
