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
from src.application.use_cases.analyze_ticker import AnalyzeTickerUseCase, AnalyzeTickerRequest, AnalyzeTickersRequest
from src.application.use_cases.compare_tickers import CompareTickersUseCase
from src.infrastructure.color_metrics_service import ColorMetricsService
# Portfolio session manager will be imported locally in get_portfolio_session_manager()
from src.domain.entities.portfolio import Portfolio
import json
from src.domain.entities.position import Position
from src.domain.entities.ticker import Ticker
from src.domain.value_objects.date_range import DateRange
from src.infrastructure.utils.date_utils import is_date_after_previous_working_day

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


# Global variables for dependency injection
_controller: Optional[PortfolioController] = None
_current_portfolio: Optional[Portfolio] = None
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


def get_portfolio_session_manager():
    """Get or initialize portfolio session manager."""
    global _portfolio_session_manager
    if _portfolio_session_manager is None:
        # Return a dummy portfolio session manager
        class DummyPortfolioSessionManager:
            def start_portfolio_session(self, portfolio_name=None):
                return "dummy-session-id"
            def end_portfolio_session(self, session_id, reason=None):
                pass
            def get_active_sessions(self):
                return []
        _portfolio_session_manager = DummyPortfolioSessionManager()
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
                # Resume the session
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
        
        
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/uploaded_portfolio_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        
        # Load portfolio using controller
        controller = get_controller()
        
        request = LoadPortfolioRequest(file_path=temp_file_path)
        response = controller._load_portfolio_use_case.execute(request)
        
        if response.success and response.portfolio:
            set_current_portfolio(response.portfolio)
            
            
            # Convert to response format
            positions = [
                PositionResponse(ticker=pos.ticker.symbol, position=float(pos.quantity))
                for pos in response.portfolio.get_positions()
            ]
            
            # Calculate total positions as sum of all position quantities
            total_positions = sum(float(pos.quantity) for pos in response.portfolio.get_positions())
            
            portfolio_response = PortfolioResponse(
                positions=positions,
                totalPositions=int(total_positions),
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
            raise HTTPException(status_code=400, detail=response.message)
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        
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
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    
    # Convert to response format
    positions = [
        PositionResponse(ticker=pos.ticker.symbol, position=float(pos.quantity))
        for pos in portfolio.get_positions()
    ]
    
    # Calculate total positions as sum of all position quantities
    total_positions = sum(float(pos.quantity) for pos in portfolio.get_positions())
    
    portfolio_response = PortfolioResponse(
        positions=positions,
        totalPositions=int(total_positions),
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
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Calculate ticker count for display
    ticker_count = len(portfolio.get_tickers())
    
    
    print(f"Portfolio analysis: {ticker_count} tickers, {start_date} to {end_date}")
    
    # Validate date range
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        
        if is_date_after_previous_working_day(end_date):
            raise HTTPException(status_code=400, detail="End date cannot be after the previous working day")
            
    except ValueError as e:
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
            raise HTTPException(status_code=400, detail=response.message)
        
        if not response.metrics:
            raise HTTPException(status_code=400, detail="No metrics calculated")
        
            
        
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
            "endValueMissing": f"${metrics.end_value_missing.amount:,.2f}",
            "dividendAmount": f"${metrics.dividend_amount.amount:,.2f}",
            "annualizedDividendYield": f"{metrics.annualized_dividend_yield.value:.2f}%",
            "totalDividendYield": f"{metrics.total_dividend_yield.value:.2f}%"
        }
        
        return {
            "success": True,
            "message": response.message,
            "data": portfolio_data,
            "warnings": {
                "missingTickers": response.missing_tickers or [],
                "tickersWithoutStartData": response.tickers_without_start_data or [],
                "firstAvailableDates": response.first_available_dates or {}
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
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/portfolio/tickers/analysis")
async def analyze_tickers(start_date: str = None, end_date: str = None):
    """Analyze individual tickers in portfolio with smart batch processing."""
    
    portfolio_uuid = get_current_portfolio_session()
    portfolio_session_manager = get_portfolio_session_manager()
    
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get portfolio info for processing
    ticker_count = len(portfolio.get_tickers())
    print(f"Ticker analysis: {ticker_count} tickers, {start_date} to {end_date}")
    
    # Validate date range
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        
        if is_date_after_previous_working_day(end_date):
            raise HTTPException(status_code=400, detail="End date cannot be after the previous working day")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        # Create date range
        date_range = DateRange(start_date, end_date)
        
        # Get controller
        controller = get_controller()
        
        # Use smart batch processing - same use case, different method
        request = AnalyzeTickersRequest(
            tickers=portfolio.get_tickers(),
            date_range=date_range,
            risk_free_rate=0.03
        )
        
        
        response = controller._analyze_ticker_use_case.execute_batch(request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        # Convert metrics to API response format
        ticker_results = []
        for metrics in response.ticker_metrics:
            ticker_data = {
                "ticker": metrics.ticker.symbol,
                "totalReturn": f"{metrics.total_return.value:.2f}%",
                "annualizedReturn": f"{metrics.annualized_return.value:.2f}%",
                "volatility": f"{metrics.volatility.value:.2f}%",
                "sharpeRatio": f"{metrics.sharpe_ratio:.3f}",
                "maxDrawdown": f"{metrics.max_drawdown.value:.2f}%",
                "sortinoRatio": f"{metrics.sortino_ratio:.3f}",
                "beta": f"{metrics.beta:.3f}",
                "var95": f"{metrics.var_95.value:.2f}%",
                "momentum12to1": f"{metrics.momentum_12_1.value:.2f}%",
                "dividendYield": f"{metrics.dividend_yield.value:.2f}%",
                "dividendAmount": f"${metrics.dividend_amount.amount:.2f}",
                "dividendFrequency": metrics.dividend_frequency,
                "annualizedDividend": f"${metrics.annualized_dividend.amount:.2f}",
                "startPrice": f"${metrics.start_price.amount:.2f}",
                "endPrice": f"${metrics.end_price.amount:.2f}",
                "hasDataAtStart": True,  # All successful tickers have data at start
                "firstAvailableDate": None  # Not available in batch response
            }
            ticker_results.append(ticker_data)
        
            
        
        # Prepare response
        response_data = {
            "success": True,
            "message": response.message,
            "data": ticker_results,
            "processingTimeSeconds": response.processing_time_seconds,
            "warnings": {
                "missingTickers": response.missing_tickers or [],
                "tickersWithoutStartData": response.tickers_without_start_data or [],
                "firstAvailableDates": response.first_available_dates or {}
            }
        }
        
        if response.failed_tickers:
            response_data["failedTickers"] = [
                {"ticker": ticker, "firstAvailableDate": None} 
                for ticker in response.failed_tickers
            ]
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticker analysis failed: {str(e)}")

# Admin API Endpoints


@app.post("/api/admin/warehouse/clear-all")
async def clear_all_warehouse():
    """Clear all warehouse data."""
    try:
        import subprocess
        import os
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(project_root, "backend", "admin", "clear_warehouse.py")
        
        # Run the warehouse clear script
        result = subprocess.run(
            ["python", script_path, "--clear-all"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
            input="yes\n"  # Auto-confirm the operation
        )
        
        if result.returncode == 0:
            return {"success": True, "message": "All warehouse data cleared successfully"}
        else:
            return {"success": False, "message": f"Error clearing warehouse: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Warehouse clearing operation timed out"}
    except Exception as e:
        return {"success": False, "message": f"Error executing warehouse clear: {str(e)}"}

@app.get("/api/admin/warehouse/stats")
async def get_warehouse_stats():
    """Get warehouse statistics."""
    try:
        import subprocess
        import os
        import json
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(project_root, "backend", "admin", "clear_warehouse.py")
        
        # Run the warehouse stats script
        result = subprocess.run(
            ["python", script_path, "--stats"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse the output to extract key statistics
            output = result.stdout
            
            # Extract basic stats from the output
            stats = {
                "tickers": [],
                "total_records": 0,
                "database_size": 0,
                "database_exists": False
            }
            
            # Try to extract ticker count and other info from the output
            lines = output.split('\n')
            for line in lines:
                if "Tickers:" in line:
                    try:
                        ticker_count = int(line.split("Tickers:")[1].strip().split()[0])
                        stats["ticker_count"] = ticker_count
                    except:
                        pass
                elif "Total Records:" in line:
                    try:
                        total_records = int(line.split("Total Records:")[1].strip().replace(",", ""))
                        stats["total_records"] = total_records
                    except:
                        pass
                elif "Database Size:" in line:
                    try:
                        size_str = line.split("Database Size:")[1].strip()
                        stats["database_size_str"] = size_str
                    except:
                        pass
            
            return {"success": True, "data": stats}
        else:
            return {"success": False, "message": f"Error getting warehouse stats: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Warehouse stats operation timed out"}
    except Exception as e:
        return {"success": False, "message": f"Error executing warehouse stats: {str(e)}"}

@app.get("/api/admin/warehouse/tickers")
async def get_warehouse_tickers(search: str = ""):
    """Get available tickers from warehouse with optional search filter."""
    try:
        import subprocess
        import os
        import json
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(project_root, "backend", "admin", "clear_warehouse.py")
        
        # Run the warehouse stats script to get ticker list
        result = subprocess.run(
            ["python", script_path, "--stats"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse the output to extract ticker list
            output = result.stdout
            tickers = []
            
            # Look for ticker list in the output
            lines = output.split('\n')
            
            # First, try to find the main tickers line
            for i, line in enumerate(lines):
                if "🏷️  Tickers:" in line or "Tickers:" in line:
                    # Look for the next line which contains the actual ticker list
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if next_line.strip().startswith("   "):
                            # Extract tickers from the indented line
                            ticker_line = next_line.strip()
                            # Split by comma and clean up
                            ticker_list = [t.strip() for t in ticker_line.split(",")]
                            # Filter out non-ticker entries (like "• Dividend Coverage")
                            tickers = [t for t in ticker_list if t and t.isalpha() and not t.startswith("•")]
                            break
            
            # If no tickers found in main section, try the breakdown section as fallback
            if not tickers:
                in_ticker_section = False
                for line in lines:
                    if "Storage Breakdown by Ticker:" in line:
                        in_ticker_section = True
                        continue
                    elif in_ticker_section and line.strip():
                        if line.startswith("   ") and ":" in line:
                            # Extract ticker name (before the colon)
                            ticker = line.strip().split(":")[0].strip()
                            if ticker and not ticker.startswith("📊") and not ticker.startswith("•"):
                                tickers.append(ticker)
                        elif not line.startswith("   "):
                            # End of ticker section
                            break
            
            # Filter tickers based on search term (if provided)
            if search and search.strip():
                search_lower = search.lower()
                tickers = [t for t in tickers if search_lower in t.lower()]
            
            # Convert to the format expected by frontend
            ticker_options = [{"value": ticker, "label": ticker} for ticker in tickers]
            
            return {"success": True, "tickers": ticker_options}
        else:
            return {"success": False, "message": f"Error getting tickers: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Ticker retrieval operation timed out"}
    except Exception as e:
        return {"success": False, "message": f"Error executing ticker retrieval: {str(e)}"}

@app.post("/api/admin/warehouse/clear-ticker")
async def clear_warehouse_ticker(request: dict):
    """Clear data for a specific ticker."""
    try:
        import subprocess
        import os
        
        ticker = request.get("ticker")
        if not ticker:
            return {"success": False, "message": "Ticker is required"}
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(project_root, "backend", "admin", "clear_warehouse.py")
        
        # Run the warehouse clear ticker script
        result = subprocess.run(
            ["python", script_path, "--clear-ticker", ticker],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
            input="yes\n"  # Auto-confirm the operation
        )
        
        if result.returncode == 0:
            return {"success": True, "message": f"Data cleared for ticker: {ticker}"}
        else:
            return {"success": False, "message": f"Error clearing ticker {ticker}: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Ticker clearing operation timed out"}
    except Exception as e:
        return {"success": False, "message": f"Error executing ticker clear: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
