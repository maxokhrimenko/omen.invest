#!/usr/bin/env python3
"""
FastAPI wrapper for Portfolio Analysis Tool
Provides REST API endpoints for frontend integration
"""

import sys
import os
import time
import uuid
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.presentation.controllers.portfolio_controller import PortfolioController
from src.infrastructure.repositories.csv_portfolio_repository import CsvPortfolioRepository
from src.infrastructure.repositories.warehouse_market_repository import WarehouseMarketRepository
from src.infrastructure.config.warehouse_config import WarehouseConfig
from src.application.use_cases.load_portfolio import LoadPortfolioUseCase, LoadPortfolioRequest
from src.application.use_cases.analyze_portfolio import (
    AnalyzePortfolioUseCase, 
    AnalyzePortfolioRequest
)
from src.application.use_cases.analyze_ticker import AnalyzeTickerUseCase, AnalyzeTickerRequest
from src.application.use_cases.compare_tickers import CompareTickersUseCase
from src.infrastructure.color_metrics_service import ColorMetricsService
from src.infrastructure.logging.logger_service import initialize_logging, get_logger_service
# Portfolio session manager will be imported locally in get_portfolio_session_manager()
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.position import Position
from src.domain.entities.ticker import Ticker
from src.domain.value_objects.date_range import DateRange

# Pydantic models for API responses
class PositionResponse(BaseModel):
    ticker: str
    position: float

class PortfolioResponse(BaseModel):
    positions: List[PositionResponse]
    totalPositions: int
    tickers: List[str]

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Analysis API",
    description="REST API for Portfolio Analysis Tool",
    version="1.0.0"
)

# Add CORS middleware
# CORS configuration - allow all localhost ports for development
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware - DISABLED in favor of portfolio-based logging
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     """Log all incoming requests with unique request IDs."""
#     # This middleware is disabled in favor of portfolio-based logging
#     # which provides better organization and context
#     return await call_next(request)

# Global variables for dependency injection
_controller: Optional[PortfolioController] = None
_current_portfolio: Optional[Portfolio] = None
_logger_service = None
_current_portfolio_session: Optional[str] = None
_portfolio_session_manager = None

# Persistent portfolio storage to survive server reloads
PORTFOLIO_STORAGE_FILE = Path("/tmp/current_portfolio.json")
PORTFOLIO_SESSION_STORAGE_FILE = Path("/tmp/current_portfolio_session.json")

def save_portfolio_to_disk(portfolio: Optional[Portfolio]) -> None:
    """Save portfolio to disk for persistence across server reloads."""
    if portfolio is None:
        if PORTFOLIO_STORAGE_FILE.exists():
            PORTFOLIO_STORAGE_FILE.unlink()
        return
    
    # Convert portfolio to serializable format
    portfolio_data = {
        "positions": [
            {
                "ticker": pos.ticker.symbol,
                "quantity": float(pos.quantity)
            }
            for pos in portfolio.get_positions()
        ]
    }
    
    with open(PORTFOLIO_STORAGE_FILE, 'w') as f:
        json.dump(portfolio_data, f)

def load_portfolio_from_disk() -> Optional[Portfolio]:
    """Load portfolio from disk if it exists."""
    if not PORTFOLIO_STORAGE_FILE.exists():
        return None
    
    try:
        with open(PORTFOLIO_STORAGE_FILE, 'r') as f:
            portfolio_data = json.load(f)
        
        # Reconstruct portfolio from saved data
        
        positions = []
        for pos_data in portfolio_data["positions"]:
            ticker = Ticker(pos_data["ticker"])
            position = Position(ticker, pos_data["quantity"])
            positions.append(position)
        
        return Portfolio(positions)
    except Exception as e:
        print(f"Error loading portfolio from disk: {e}")
        return None

def get_logger_service():
    """Get or initialize logger service."""
    global _logger_service
    if _logger_service is None:
        # Use absolute path to project root logs directory
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(project_root, "logs")
        _logger_service = initialize_logging(logs_dir)
    return _logger_service

def get_portfolio_session_manager():
    """Get or initialize portfolio session manager."""
    global _portfolio_session_manager
    if _portfolio_session_manager is None:
        from src.infrastructure.logging.portfolio_session_manager import initialize_portfolio_session_manager
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(project_root, "logs")
        _portfolio_session_manager = initialize_portfolio_session_manager(logs_dir)
    return _portfolio_session_manager

def get_controller() -> PortfolioController:
    """Get or create portfolio controller instance."""
    global _controller
    if _controller is None:
        # Set up dependency injection (same as main.py)
        portfolio_repo = CsvPortfolioRepository()
        
        warehouse_config = WarehouseConfig()
        market_repo = WarehouseMarketRepository(
            warehouse_enabled=warehouse_config.is_enabled(),
            warehouse_db_path=warehouse_config.get_db_path()
        )
        
        color_service = ColorMetricsService()
        
        load_portfolio_use_case = LoadPortfolioUseCase(portfolio_repo)
        analyze_portfolio_use_case = AnalyzePortfolioUseCase(market_repo)
        analyze_ticker_use_case = AnalyzeTickerUseCase(market_repo)
        compare_tickers_use_case = CompareTickersUseCase(analyze_ticker_use_case)
        
        _controller = PortfolioController(
            load_portfolio_use_case,
            analyze_portfolio_use_case,
            analyze_ticker_use_case,
            compare_tickers_use_case,
            color_service
        )
    
    return _controller

def get_current_portfolio() -> Optional[Portfolio]:
    """Get current portfolio from controller."""
    global _current_portfolio
    
    # If portfolio is None (e.g., after server reload), try to load from disk
    if _current_portfolio is None:
        _current_portfolio = load_portfolio_from_disk()
        
        # If portfolio was loaded from disk, also try to resume the session
        if _current_portfolio is not None and _current_portfolio_session is None:
            session_uuid = load_portfolio_session_from_disk()
            if session_uuid:
                # Resume the session without creating a new log file
                portfolio_session_manager = get_portfolio_session_manager()
                # Check if session still exists in manager, if not, create a new one
                if session_uuid not in portfolio_session_manager.get_active_sessions():
                    # Create a new session with the same UUID for continuity
                    portfolio_session_manager.start_portfolio_session(
                        portfolio_name=f"resumed-{session_uuid}"
                    )
                set_current_portfolio_session(session_uuid)
    
    return _current_portfolio

def set_current_portfolio(portfolio: Optional[Portfolio]) -> None:
    """Set current portfolio."""
    global _current_portfolio
    _current_portfolio = portfolio
    
    # Save to disk for persistence across server reloads
    save_portfolio_to_disk(portfolio)

def get_current_portfolio_session() -> Optional[str]:
    """Get current portfolio session UUID."""
    return _current_portfolio_session

def set_current_portfolio_session(session_uuid: Optional[str]) -> None:
    """Set current portfolio session UUID."""
    global _current_portfolio_session
    _current_portfolio_session = session_uuid
    
    # Save session to disk for persistence
    save_portfolio_session_to_disk(session_uuid)

def save_portfolio_session_to_disk(session_uuid: Optional[str]) -> None:
    """Save portfolio session to disk for persistence across server reloads."""
    if session_uuid is None:
        if PORTFOLIO_SESSION_STORAGE_FILE.exists():
            PORTFOLIO_SESSION_STORAGE_FILE.unlink()
        return
    
    session_data = {"session_uuid": session_uuid}
    with open(PORTFOLIO_SESSION_STORAGE_FILE, 'w') as f:
        json.dump(session_data, f)

def load_portfolio_session_from_disk() -> Optional[str]:
    """Load portfolio session from disk if it exists."""
    if not PORTFOLIO_SESSION_STORAGE_FILE.exists():
        return None
    
    try:
        with open(PORTFOLIO_SESSION_STORAGE_FILE, 'r') as f:
            session_data = json.load(f)
        return session_data.get("session_uuid")
    except Exception as e:
        print(f"Error loading portfolio session from disk: {e}")
        return None

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.post("/portfolio/upload")
async def upload_portfolio(file: UploadFile = File(...)):
    """Upload portfolio CSV file."""
    try:
        # Start a new portfolio session
        portfolio_session_manager = get_portfolio_session_manager()
        portfolio_uuid = portfolio_session_manager.start_portfolio_session(
            portfolio_name=file.filename.replace('.csv', '') if file.filename else None
        )
        set_current_portfolio_session(portfolio_uuid)
        
        # Log file upload start
        portfolio_session_manager.log_portfolio_operation(
            portfolio_uuid=portfolio_uuid,
            operation="portfolio_upload",
            success=True,
            details={
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file.size if hasattr(file, 'size') else "unknown"
            }
        )
        
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error="Invalid file type",
                operation="portfolio_upload",
                details={"filename": file.filename, "expected": "CSV"}
            )
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/uploaded_portfolio_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Log file operation
        portfolio_session_manager.log_portfolio_operation(
            portfolio_uuid=portfolio_uuid,
            operation="file_upload",
            success=True,
            details={"size_bytes": len(content), "file_path": temp_file_path}
        )
        
        # Load portfolio using controller
        controller = get_controller()
        
        request = LoadPortfolioRequest(file_path=temp_file_path)
        response = controller._load_portfolio_use_case.execute(request)
        
        if response.success and response.portfolio:
            set_current_portfolio(response.portfolio)
            
            # Log successful portfolio load
            portfolio_session_manager.log_portfolio_operation(
                portfolio_uuid=portfolio_uuid,
                operation="portfolio_load",
                success=True,
                details={
                    "positions_count": len(response.portfolio.get_positions()),
                    "tickers": [t.symbol for t in response.portfolio.get_tickers()]
                }
            )
            
            # Convert to response format
            positions = [
                PositionResponse(ticker=pos.ticker.symbol, position=float(pos.quantity))
                for pos in response.portfolio.get_positions()
            ]
            
            portfolio_response = PortfolioResponse(
                positions=positions,
                totalPositions=len(response.portfolio.get_positions()),
                tickers=[t.symbol for t in response.portfolio.get_tickers()]
            )
            
            return {
                "success": True,
                "message": (
                    f"Portfolio loaded successfully with "
                    f"{len(response.portfolio.get_positions())} positions"
                ),
                "portfolio": portfolio_response.model_dump()
            }
        else:
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error="Portfolio load failed",
                operation="portfolio_load",
                details={"message": response.message}
            )
            raise HTTPException(status_code=400, detail=response.message)
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors
        portfolio_uuid = get_current_portfolio_session()
        if portfolio_uuid:
            portfolio_session_manager = get_portfolio_session_manager()
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error=f"Unexpected error: {str(e)}",
                operation="portfolio_upload",
                details={"filename": file.filename if file else "unknown"}
            )
        
        import traceback
        print("FULL TRACEBACK:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/portfolio")
async def get_portfolio():
    """Get current portfolio."""
    portfolio_uuid = get_current_portfolio_session()
    portfolio_session_manager = get_portfolio_session_manager()
    
    portfolio = get_current_portfolio()
    
    if not portfolio:
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error="No portfolio loaded",
                operation="get_portfolio"
            )
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Log portfolio retrieval
    if portfolio_uuid:
        portfolio_session_manager.log_portfolio_operation(
            portfolio_uuid=portfolio_uuid,
            operation="get_portfolio",
            success=True,
            details={
                "positions_count": len(portfolio.get_positions()),
                "tickers": [t.symbol for t in portfolio.get_tickers()]
            }
        )
    
    # Convert to response format
    positions = [
        PositionResponse(ticker=pos.ticker.symbol, position=float(pos.quantity))
        for pos in portfolio.get_positions()
    ]
    
    portfolio_response = PortfolioResponse(
        positions=positions,
        totalPositions=len(portfolio.get_positions()),
        tickers=[t.symbol for t in portfolio.get_tickers()]
    )
    
    return portfolio_response

@app.delete("/portfolio")
async def clear_portfolio():
    """Clear current portfolio."""
    portfolio_uuid = get_current_portfolio_session()
    
    # End the portfolio session if it exists
    if portfolio_uuid:
        portfolio_session_manager = get_portfolio_session_manager()
        portfolio_session_manager.end_portfolio_session(portfolio_uuid, reason="portfolio_cleared")
        set_current_portfolio_session(None)
    
    set_current_portfolio(None)  # This will also clear disk storage
    return ApiResponse(success=True, message="Portfolio cleared successfully")

@app.get("/portfolio/analysis")
async def analyze_portfolio(start_date: str = None, end_date: str = None):
    """Analyze current portfolio with date range parameters."""
    portfolio_uuid = get_current_portfolio_session()
    portfolio_session_manager = get_portfolio_session_manager()
    
    portfolio = get_current_portfolio()
    
    if not portfolio:
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error="No portfolio loaded",
                operation="portfolio_analysis"
            )
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Log portfolio analysis start
    ticker_count = len(portfolio.get_tickers())
    if portfolio_uuid:
        portfolio_session_manager.log_portfolio_operation(
            portfolio_uuid=portfolio_uuid,
            operation="portfolio_analysis",
            success=True,
            details={
                "ticker_count": ticker_count,
                "start_date": start_date,
                "end_date": end_date
            }
        )
    
    print(f"Portfolio analysis: {ticker_count} tickers, {start_date} to {end_date}")
    
    # Validate date range
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt > end_dt:
            if portfolio_uuid:
                portfolio_session_manager.log_portfolio_error(
                    portfolio_uuid=portfolio_uuid,
                    error="Invalid date range",
                    operation="portfolio_analysis",
                    details={"start_date": start_date, "end_date": end_date}
                )
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        
        if end_dt > datetime.now():
            if portfolio_uuid:
                portfolio_session_manager.log_portfolio_error(
                    portfolio_uuid=portfolio_uuid,
                    error="End date in future",
                    operation="portfolio_analysis",
                    details={"end_date": end_date}
                )
            raise HTTPException(status_code=400, detail="End date cannot be in the future")
            
    except ValueError as e:
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error="Invalid date format",
                operation="portfolio_analysis",
                details={"start_date": start_date, "end_date": end_date, "error": str(e)}
            )
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        # Import required classes
        
        # Create date range
        date_range = DateRange(start_date, end_date)
        
        # Get controller and run analysis
        controller = get_controller()
        request = AnalyzePortfolioRequest(
            portfolio=portfolio,
            date_range=date_range,
            risk_free_rate=0.03
        )
        
        response = controller._analyze_portfolio_use_case.execute(request)
        
        if not response.success:
            if portfolio_uuid:
                portfolio_session_manager.log_portfolio_error(
                    portfolio_uuid=portfolio_uuid,
                    error="Portfolio analysis failed",
                    operation="portfolio_analysis",
                    details={"message": response.message}
                )
            raise HTTPException(status_code=400, detail=response.message)
        
        if not response.metrics:
            if portfolio_uuid:
                portfolio_session_manager.log_portfolio_error(
                    portfolio_uuid=portfolio_uuid,
                    error="No metrics calculated",
                    operation="portfolio_analysis",
                    details={"message": "Analysis completed but no metrics returned"}
                )
            raise HTTPException(status_code=400, detail="No metrics calculated")
        
        # Log successful analysis
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_operation(
                portfolio_uuid=portfolio_uuid,
                operation="portfolio_analysis_complete",
                success=True,
                details={
                    "missing_tickers": (
                        len(response.missing_tickers) if response.missing_tickers else 0
                    ),
                    "tickers_without_start_data": (
                        len(response.tickers_without_start_data) 
                        if response.tickers_without_start_data else 0
                    )
                }
            )
        
        # Convert metrics to API response format
        metrics = response.metrics
        portfolio_data = {
            "totalReturn": f"{metrics.total_return.value:.2f}%",
            "annualizedReturn": f"{metrics.annualized_return.value:.2f}%",
            "volatility": f"{metrics.volatility.value:.2f}%",
            "sharpeRatio": f"{metrics.sharpe_ratio:.3f}",
            "maxDrawdown": f"{metrics.max_drawdown.value:.2f}%",
            "sortinoRatio": f"{metrics.sortino_ratio:.3f}",
            "calmarRatio": f"{metrics.calmar_ratio:.3f}",
            "var95": f"{metrics.var_95.value:.2f}%",
            "beta": f"{metrics.beta:.3f}",
            "startValue": f"${metrics.start_value.amount:,.2f}",
            "endValue": f"${metrics.end_value.amount:,.2f}",
            "endValueAnalysis": f"${metrics.end_value_analysis.amount:,.2f}",
            "endValueMissing": f"${metrics.end_value_missing.amount:,.2f}"
        }
        
        return {
            "success": True,
            "message": response.message,
            "data": portfolio_data,
            "warnings": {
                "missingTickers": response.missing_tickers or [],
                "tickersWithoutStartData": response.tickers_without_start_data or []
            },
            "timeSeriesData": {
                "portfolioValues": response.portfolio_values_over_time or {},
                "sp500Values": response.sp500_values_over_time or {},
                "nasdaqValues": response.nasdaq_values_over_time or {}
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error=f"Analysis failed: {str(e)}",
                operation="portfolio_analysis",
                details={"start_date": start_date, "end_date": end_date}
            )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/portfolio/tickers/analysis")
async def analyze_tickers(start_date: str = None, end_date: str = None):
    """Analyze individual tickers in portfolio with date range parameters."""
    import asyncio
    
    portfolio_uuid = get_current_portfolio_session()
    portfolio_session_manager = get_portfolio_session_manager()
    
    portfolio = get_current_portfolio()
    
    if not portfolio:
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error="No portfolio loaded",
                operation="ticker_analysis"
            )
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Log portfolio info for debugging
    ticker_count = len(portfolio.get_tickers())
    print(f"Ticker analysis: {ticker_count} tickers, {start_date} to {end_date}")
    
    # Log ticker analysis start
    if portfolio_uuid:
        portfolio_session_manager.log_portfolio_operation(
            portfolio_uuid=portfolio_uuid,
            operation="ticker_analysis",
            success=True,
            details={
                "ticker_count": ticker_count,
                "start_date": start_date,
                "end_date": end_date
            }
        )
    
    # Validate date range
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        
        if end_dt > datetime.now():
            raise HTTPException(status_code=400, detail="End date cannot be in the future")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        # Import required classes
        
        # Create date range
        date_range = DateRange(start_date, end_date)
        
        # Get controller
        controller = get_controller()
        
        # Define analysis function for timeout handling
        def analyze_ticker_sync(ticker):
            request = AnalyzeTickerRequest(
                ticker=ticker,
                date_range=date_range,
                risk_free_rate=0.03
            )
            return controller._analyze_ticker_use_case.execute(request)
        
        # Analyze each ticker with timeout and progress tracking
        ticker_results = []
        failed_tickers = []
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=min(10, ticker_count)) as executor:
            # Submit all ticker analysis tasks
            future_to_ticker = {
                executor.submit(analyze_ticker_sync, ticker): ticker 
                for ticker in portfolio.get_tickers()
            }
            
            # Process results with timeout and progress tracking
            for future in future_to_ticker:
                ticker = future_to_ticker[future]
                processed_count += 1
                
                # Log progress for large portfolios
                if ticker_count > 20 and processed_count % 10 == 0:
                    print(
                        f"Progress: {processed_count}/{ticker_count} tickers processed "
                        f"({processed_count/ticker_count*100:.1f}%)"
                    )
                
                try:
                    # Use a reasonable timeout per ticker (30 seconds total / ticker count)
                    per_ticker_timeout = max(5, 30 / ticker_count)  # At least 5 seconds per ticker
                    response = future.result(timeout=per_ticker_timeout)
                    
                    if response.success and response.metrics:
                        metrics = response.metrics
                        ticker_data = {
                            "ticker": ticker.symbol,
                            "totalReturn": f"{metrics.total_return.value:.2f}%",
                            "annualizedReturn": f"{metrics.annualized_return.value:.2f}%",
                            "volatility": f"{metrics.volatility.value:.2f}%",
                            "sharpeRatio": f"{metrics.sharpe_ratio:.3f}",
                            "maxDrawdown": f"{metrics.max_drawdown.value:.2f}%",
                            "sortinoRatio": f"{metrics.sortino_ratio:.3f}",
                            "beta": f"{metrics.beta:.3f}",
                            "var95": f"{metrics.var_95.value:.2f}%",
                            "momentum12_1": f"{metrics.momentum_12_1.value:.2f}%",
                            "dividendYield": f"{metrics.dividend_yield.value:.2f}%",
                            "dividendAmount": f"${metrics.dividend_amount.amount:.2f}",
                            "dividendFrequency": metrics.dividend_frequency,
                            "annualizedDividend": f"${metrics.annualized_dividend.amount:.2f}",
                            "startPrice": f"${metrics.start_price.amount:.2f}",
                            "endPrice": f"${metrics.end_price.amount:.2f}",
                            "hasDataAtStart": response.has_data_at_start,
                            "firstAvailableDate": response.first_available_date
                        }
                        ticker_results.append(ticker_data)
                    else:
                        # Even for failed tickers, try to get first_available_date if available
                        failed_ticker_info = {
                            "ticker": ticker.symbol,
                            "firstAvailableDate": response.first_available_date if hasattr(response, 'first_available_date') else None
                        }
                        failed_tickers.append(failed_ticker_info)
                        
                except FutureTimeoutError:
                    failed_tickers.append({"ticker": ticker.symbol, "firstAvailableDate": None})
                except Exception as e:
                    failed_tickers.append({"ticker": ticker.symbol, "firstAvailableDate": None})
        
        # Log ticker analysis completion
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_operation(
                portfolio_uuid=portfolio_uuid,
                operation="ticker_analysis_complete",
                success=True,
                details={
                    "successful_tickers": len(ticker_results),
                    "failed_tickers": len(failed_tickers),
                    "total_tickers": ticker_count
                }
            )
        
        # Prepare response
        response_data = {
            "success": True,
            "message": f"Analyzed {len(ticker_results)} tickers successfully",
            "data": ticker_results
        }
        
        if failed_tickers:
            response_data["warnings"] = (
                f"Failed to analyze {len(failed_tickers)} tickers: "
                f"{', '.join([ticker['ticker'] if isinstance(ticker, dict) else ticker for ticker in failed_tickers])}"
            )
            response_data["failedTickers"] = failed_tickers
        
        return response_data
        
    except Exception as e:
        if portfolio_uuid:
            portfolio_session_manager.log_portfolio_error(
                portfolio_uuid=portfolio_uuid,
                error=f"Ticker analysis failed: {str(e)}",
                operation="ticker_analysis",
                details={"start_date": start_date, "end_date": end_date}
            )
        raise HTTPException(status_code=500, detail=f"Ticker analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
