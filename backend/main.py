#!/usr/bin/env python3
"""
Portfolio Analysis Tool - Main Entry Point
Version 4.1.2 - Full-Stack Repository Restructure

This application provides comprehensive portfolio analysis
with interactive CLI interface following clean architecture principles.

"""

import sys
import os
import atexit

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.presentation.cli.menu import MainMenu
from src.presentation.controllers.portfolio_controller import PortfolioController
from src.infrastructure.repositories.csv_portfolio_repository import CsvPortfolioRepository
from src.infrastructure.repositories.warehouse_market_repository import WarehouseMarketRepository
from src.infrastructure.config.warehouse_config import WarehouseConfig
from src.application.use_cases.load_portfolio import LoadPortfolioUseCase
from src.application.use_cases.analyze_portfolio import AnalyzePortfolioUseCase
from src.application.use_cases.analyze_ticker import AnalyzeTickerUseCase
from src.application.use_cases.compare_tickers import CompareTickersUseCase
from src.infrastructure.logging.logger_service import initialize_logging
from src.infrastructure.color_metrics_service import ColorMetricsService


def setup_dependencies():
    """Set up dependency injection container."""
    # Infrastructure layer
    portfolio_repo = CsvPortfolioRepository()
    
    # Warehouse configuration
    warehouse_config = WarehouseConfig()
    market_repo = WarehouseMarketRepository(
        warehouse_enabled=warehouse_config.is_enabled(),
        warehouse_db_path=warehouse_config.get_db_path()
    )
    
    color_service = ColorMetricsService()
    
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
        compare_tickers_use_case,
        color_service
    )
    
    return controller

def main():
    """Main application entry point."""
    # Initialize logging system
    logger_service = initialize_logging("logs")
    session_id = logger_service.start_session()
    
    # Register cleanup function
    def cleanup():
        logger_service.end_session()
    
    atexit.register(cleanup)
    
    # Get logger for main application
    logger = logger_service.get_logger("main")
    
    try:
        logger.info("=== PORTFOLIO ANALYSIS TOOL STARTING ===")
        logger.info(f"Session ID: {session_id}")
        print("🚀 Starting Portfolio Analysis Tool v4.1.1...")
        print("📦 Initializing components...")
        
        logger.info("Setting up dependency injection")
        controller = setup_dependencies()
        menu = MainMenu(controller)
        
        logger.info("Application initialization completed successfully")
        print("✅ Application ready!")
        
        # Log user interaction start
        logger.info("Starting user interaction loop")
        menu.show()
        
        logger.info("User interaction completed normally")
        
    except KeyboardInterrupt:
        logger.warning("Application interrupted by user (KeyboardInterrupt)")
        print("\n\n⚠️  Application interrupted by user.")
        print("👋 Goodbye!")
        return 1
    except Exception as e:
        logger.error(f"Fatal error in main application: {str(e)}", exc_info=True)
        print(f"\n💥 Fatal error: {str(e)}")
        print("📞 Please check your configuration and try again.")
        return 1
    finally:
        logger.info("=== PORTFOLIO ANALYSIS TOOL SHUTTING DOWN ===")
        cleanup()
    
    return 0

if __name__ == "__main__":
    exit(main())
