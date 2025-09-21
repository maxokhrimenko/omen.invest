#!/usr/bin/env python3
"""
Portfolio Analysis Tool - Main Entry Point
Version 4.0.0 - Major Architecture Refactoring

This application provides comprehensive portfolio analysis
with interactive CLI interface following clean architecture principles.

Major changes in v4.0.0:
- Complete refactoring with Clean Architecture
- Interactive CLI interface
- Comprehensive test suite (38 tests)
- SOLID principles implementation
- Enhanced error handling and user experience
"""

import sys
import os

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.presentation.cli.menu import MainMenu
from src.presentation.controllers.portfolio_controller import PortfolioController
from src.infrastructure.repositories.csv_portfolio_repository import CsvPortfolioRepository
from src.infrastructure.repositories.yfinance_market_repository import YFinanceMarketRepository
from src.application.use_cases.load_portfolio import LoadPortfolioUseCase
from src.application.use_cases.analyze_portfolio import AnalyzePortfolioUseCase
from src.application.use_cases.analyze_ticker import AnalyzeTickerUseCase
from src.application.use_cases.compare_tickers import CompareTickersUseCase


def setup_dependencies():
    """Set up dependency injection container."""
    # Infrastructure layer
    portfolio_repo = CsvPortfolioRepository()
    market_repo = YFinanceMarketRepository()
    
    # Application layer
    load_portfolio_use_case = LoadPortfolioUseCase(portfolio_repo)
    analyze_portfolio_use_case = AnalyzePortfolioUseCase(market_repo)
    analyze_ticker_use_case = AnalyzeTickerUseCase(market_repo)
    compare_tickers_use_case = CompareTickersUseCase(analyze_ticker_use_case)
    
    # Presentation layer
    controller = PortfolioController(
        load_portfolio_use_case,
        analyze_portfolio_use_case,
        analyze_ticker_use_case,
        compare_tickers_use_case
    )
    
    return controller

def main():
    """Main application entry point."""
    try:
        print("🚀 Starting Portfolio Analysis Tool v4.0.0...")
        print("📦 Initializing components...")
        
        controller = setup_dependencies()
        menu = MainMenu(controller)
        
        print("✅ Application ready!")
        menu.show()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user.")
        print("👋 Goodbye!")
        return 1
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        print("📞 Please check your configuration and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
