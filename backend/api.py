#!/usr/bin/env python3
"""
FastAPI wrapper for Portfolio Analysis Tool
Provides REST API endpoints for frontend integration
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.presentation.controllers.main_controller import MainController
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
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.position import Position
from src.domain.entities.ticker import Ticker
from src.domain.value_objects.date_range import DateRange
from src.infrastructure.utils.date_utils import is_date_after_previous_working_day, get_previous_working_day_string

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

# Compare Tickers API Response Models
class TickerComparisonData(BaseModel):
    metrics: List[dict]  # TickerAnalysis data
    bestPerformer: dict  # TickerAnalysis data
    worstPerformer: dict  # TickerAnalysis data
    bestSharpe: dict  # TickerAnalysis data
    lowestRisk: dict  # TickerAnalysis data

# Helper functions
def _convert_metrics_to_api(metrics):
    """Convert metrics to API format."""
    return {
        "ticker": metrics.ticker.symbol,
        "annualizedReturn": f"{metrics.annualized_return.value:.2f}%",
        "sharpeRatio": f"{metrics.sharpe_ratio:.2f}",
        "volatility": f"{metrics.volatility.value:.2f}%",
        "maxDrawdown": f"{metrics.max_drawdown.value:.2f}%",
        "sortinoRatio": f"{metrics.sortino_ratio:.2f}",
        "calmarRatio": f"{metrics.calmar_ratio:.2f}",
        "ulcerIndex": f"{metrics.ulcer_index:.4f}",
        "timeUnderWater": f"{metrics.time_under_water:.4f}",
        "cvar95": f"{metrics.cvar_95:.2f}",
        "correlationToPortfolio": f"{metrics.correlation_to_portfolio:.2f}",
        "riskContributionPercent": f"{metrics.risk_contribution_percent:.2f}%"
    }

def _get_sort_value(metric, sort_key):
    """Get sort value from metric attribute."""
    value = getattr(metric, sort_key)
    return value.value if hasattr(value, 'value') else value

def _get_top_performers(metrics_list, sort_key, reverse=True, limit=5):
    """Get top performers sorted by specified criteria."""
    sorted_metrics = sorted(metrics_list, 
                          key=lambda metric: _get_sort_value(metric, sort_key), 
                          reverse=reverse)
    return [_convert_metrics_to_api(metric) for metric in sorted_metrics[:limit]]

async def _save_uploaded_file(file: UploadFile, temp_file_path: str) -> None:
    """Save uploaded file to temporary location."""
    with open(temp_file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

def _create_portfolio_response(portfolio: Portfolio) -> PortfolioResponse:
    """Create portfolio response from portfolio object."""
    positions = [
        PositionResponse(ticker=pos.ticker.symbol, position=float(pos.quantity))
        for pos in portfolio.get_positions()
    ]
    
    total_positions = sum(float(pos.quantity) for pos in portfolio.get_positions())
    
    return PortfolioResponse(
        positions=positions,
        totalPositions=int(total_positions),
        tickers=[t.symbol for t in portfolio.get_tickers()]
    )

def _get_default_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    """Get default date range if not provided."""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    return start_date, end_date

def _validate_date_range(start_date: str, end_date: str) -> None:
    """Validate date range parameters."""
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        
        if is_date_after_previous_working_day(end_date):
            previous_working_day = get_previous_working_day_string()
            raise HTTPException(
                status_code=400, 
                detail=f"End date cannot be after the previous working day ({previous_working_day}). Please use a date on or before {previous_working_day}."
            )
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

def _convert_metrics_to_api_response(metrics) -> dict:
    """Convert metrics to API response format."""
    return {
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

class CompareTickersResponse(BaseModel):
    success: bool
    message: str
    data: TickerComparisonData
    warnings: dict
    failedTickers: Optional[List[dict]] = None

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
_controller: Optional[MainController] = None
_current_portfolio: Optional[Portfolio] = None

# Persistent portfolio storage to survive server reloads
PORTFOLIO_STORAGE_FILE = Path("/tmp/current_portfolio.json")

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



def get_controller() -> MainController:
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
        compare_tickers_use_case = CompareTickersUseCase(analyze_ticker_use_case, market_repo)
        
        _controller = MainController(
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
    
    return _current_portfolio

def set_current_portfolio(portfolio: Optional[Portfolio]) -> None:
    """Set current portfolio."""
    global _current_portfolio
    _current_portfolio = portfolio
    
    # Save to disk for persistence across server reloads
    save_portfolio_to_disk(portfolio)


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@app.post("/portfolio/upload")
async def upload_portfolio(file: UploadFile = File(...)):
    """Upload portfolio CSV file."""
    temp_file_path = None
    try:
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/uploaded_portfolio_{file.filename}"
        await _save_uploaded_file(file, temp_file_path)
        
        # Load portfolio using controller
        controller = get_controller()
        request = LoadPortfolioRequest(file_path=temp_file_path)
        response = controller._load_portfolio_use_case.execute(request)
        
        if response.success and response.portfolio:
            set_current_portfolio(response.portfolio)
            portfolio_response = _create_portfolio_response(response.portfolio)
            
            return {
                "success": True,
                "message": f"Portfolio loaded successfully with {len(response.portfolio.get_positions())} positions",
                "portfolio": portfolio_response.model_dump()
            }
        else:
            raise HTTPException(status_code=400, detail=response.message)
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("FULL TRACEBACK:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/portfolio")
async def get_portfolio():
    """Get current portfolio."""
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    return _create_portfolio_response(portfolio)

@app.delete("/portfolio")
async def clear_portfolio():
    """Clear current portfolio."""
    set_current_portfolio(None)  # This will also clear disk storage
    return ApiResponse(success=True, message="Portfolio cleared successfully")

@app.get("/portfolio/analysis")
async def analyze_portfolio(start_date: str = None, end_date: str = None):
    """Analyze current portfolio with date range parameters."""
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Set default date range if not provided
    start_date, end_date = _get_default_date_range(start_date, end_date)
    
    # Validate date range
    _validate_date_range(start_date, end_date)
    
    try:
        # Create date range and run analysis
        date_range = DateRange(start_date, end_date)
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
        portfolio_data = _convert_metrics_to_api_response(response.metrics)
        
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
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/portfolio/tickers/analysis")
async def analyze_tickers(start_date: str = None, end_date: str = None):
    """Analyze individual tickers in portfolio with smart batch processing."""
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Set default date range if not provided
    start_date, end_date = _get_default_date_range(start_date, end_date)
    
    # Validate date range
    _validate_date_range(start_date, end_date)
    
    try:
        # Create date range and run analysis
        date_range = DateRange(start_date, end_date)
        controller = get_controller()
        
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
            # Find position quantity for this ticker
            position_quantity = 0
            for pos in portfolio.get_positions():
                if pos.ticker.symbol == metrics.ticker.symbol:
                    position_quantity = float(pos.quantity)
                    break
            
            # Calculate market value (position * end price)
            end_price_value = float(metrics.end_price.amount)
            market_value = position_quantity * end_price_value
            
            ticker_data = {
                "ticker": metrics.ticker.symbol,
                "totalReturn": f"{metrics.total_return.value:.2f}%",
                "annualizedReturn": f"{metrics.annualized_return.value:.2f}%",
                "volatility": f"{metrics.volatility.value:.2f}%",
                "sharpeRatio": f"{metrics.sharpe_ratio:.3f}",
                "maxDrawdown": f"{metrics.max_drawdown.value:.2f}%",
                "sortinoRatio": f"{metrics.sortino_ratio:.3f}",
                "calmarRatio": f"{metrics.calmar_ratio:.2f}",
                "ulcerIndex": f"{metrics.ulcer_index:.4f}",
                "timeUnderWater": f"{metrics.time_under_water:.2f}",
                "cvar95": f"{metrics.cvar_95:.2f}",
                "correlationToPortfolio": f"{metrics.correlation_to_portfolio:.2f}",
                "riskContributionAbsolute": f"{metrics.risk_contribution_absolute:.4f}",
                "riskContributionPercent": f"{metrics.risk_contribution_percent:.2f}%",
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
                "firstAvailableDate": None,  # Not available in batch response
                "position": position_quantity,
                "marketValue": f"${market_value:,.2f}"
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

@app.post("/portfolio/tickers/compare")
async def compare_tickers(request_data: dict):
    """Compare tickers in portfolio."""
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Extract date range from request
    start_date = request_data.get('start_date')
    end_date = request_data.get('end_date')
    
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="start_date and end_date are required")
    
    # Set default date range if not provided
    start_date, end_date = _get_default_date_range(start_date, end_date)
    
    # Validate date range
    _validate_date_range(start_date, end_date)
    
    try:
        # Create date range and run comparison
        date_range = DateRange(start_date, end_date)
        controller = get_controller()
        
        # Use compare tickers use case
        from src.application.use_cases.compare_tickers import CompareTickersRequest
        request = CompareTickersRequest(
            tickers=portfolio.get_tickers(),
            date_range=date_range,
            risk_free_rate=0.03
        )
        
        response = controller._compare_tickers_use_case.execute(request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        # Convert comparison data to API response format
        comparison_data = response.comparison
        
        # Convert metrics to API format
        metrics_data = []
        for metrics in comparison_data.metrics:
            # Find position quantity for this ticker
            position_quantity = 0
            for pos in portfolio.get_positions():
                if pos.ticker.symbol == metrics.ticker.symbol:
                    position_quantity = float(pos.quantity)
                    break
            
            # Calculate market value (position * end price)
            end_price_value = float(metrics.end_price.amount)
            market_value = position_quantity * end_price_value
            
            ticker_data = {
                "ticker": metrics.ticker.symbol,
                "totalReturn": f"{metrics.total_return.value:.2f}%",
                "annualizedReturn": f"{metrics.annualized_return.value:.2f}%",
                "volatility": f"{metrics.volatility.value:.2f}%",
                "sharpeRatio": f"{metrics.sharpe_ratio:.2f}",
                "maxDrawdown": f"{metrics.max_drawdown.value:.2f}%",
                "sortinoRatio": f"{metrics.sortino_ratio:.2f}",
                "beta": f"{metrics.beta:.2f}",
                "var95": f"{metrics.var_95.value:.2f}%",
                "momentum12to1": f"{metrics.momentum_12_1.value:.2f}%",
                "dividendYield": f"{metrics.dividend_yield.value:.2f}%",
                "dividendAmount": f"${metrics.dividend_amount.amount:.2f}",
                "dividendFrequency": metrics.dividend_frequency,
                "annualizedDividend": f"${metrics.annualized_dividend.amount:.2f}",
                "startPrice": f"${metrics.start_price.amount:.2f}",
                "endPrice": f"${metrics.end_price.amount:.2f}",
                "hasDataAtStart": True,
                "position": position_quantity,
                "marketValue": f"${market_value:.2f}",
                # Advanced metrics
                "calmarRatio": f"{metrics.calmar_ratio:.2f}",
                "ulcerIndex": f"{metrics.ulcer_index:.4f}",
                "timeUnderWater": f"{metrics.time_under_water:.2f}",
                "cvar95": f"{metrics.cvar_95:.2f}",
                "correlationToPortfolio": f"{metrics.correlation_to_portfolio:.2f}",
                "riskContributionAbsolute": f"{metrics.risk_contribution_absolute:.4f}",
                "riskContributionPercent": f"{metrics.risk_contribution_percent:.2f}%"
            }
            metrics_data.append(ticker_data)
        
        # Get top 5 performers in each category
        best_performers = _get_top_performers(comparison_data.metrics, 'annualized_return', True, 5)
        worst_performers = _get_top_performers(comparison_data.metrics, 'annualized_return', False, 5)
        best_sharpe = _get_top_performers(comparison_data.metrics, 'sharpe_ratio', True, 5)
        lowest_risk = _get_top_performers(comparison_data.metrics, 'volatility', False, 5)
        
        # Advanced metrics rankings
        best_calmar = _get_top_performers(comparison_data.metrics, 'calmar_ratio', True, 5)  # Higher is better
        worst_calmar = _get_top_performers(comparison_data.metrics, 'calmar_ratio', False, 5)
        best_sortino = _get_top_performers(comparison_data.metrics, 'sortino_ratio', True, 5)  # Higher is better
        worst_sortino = _get_top_performers(comparison_data.metrics, 'sortino_ratio', False, 5)
        best_max_drawdown = _get_top_performers(comparison_data.metrics, 'max_drawdown', True, 5)  # Less negative is better
        worst_max_drawdown = _get_top_performers(comparison_data.metrics, 'max_drawdown', False, 5)  # More negative is worse
        best_ulcer = _get_top_performers(comparison_data.metrics, 'ulcer_index', False, 5)  # Lower is better
        worst_ulcer = _get_top_performers(comparison_data.metrics, 'ulcer_index', True, 5)
        best_time_under_water = _get_top_performers(comparison_data.metrics, 'time_under_water', False, 5)  # Lower is better
        worst_time_under_water = _get_top_performers(comparison_data.metrics, 'time_under_water', True, 5)
        best_cvar = _get_top_performers(comparison_data.metrics, 'cvar_95', False, 5)  # Lower is better (more negative)
        worst_cvar = _get_top_performers(comparison_data.metrics, 'cvar_95', True, 5)
        best_correlation = _get_top_performers(comparison_data.metrics, 'correlation_to_portfolio', False, 5)  # Lower absolute correlation is better
        worst_correlation = _get_top_performers(comparison_data.metrics, 'correlation_to_portfolio', True, 5)
        best_risk_contribution = _get_top_performers(comparison_data.metrics, 'risk_contribution_percent', False, 5)  # Lower is better
        worst_risk_contribution = _get_top_performers(comparison_data.metrics, 'risk_contribution_percent', True, 5)
        
        # Build response data
        response_data = {
            "success": response.success,
            "message": response.message,
            "data": {
                "metrics": metrics_data,
                "bestPerformers": best_performers,
                "worstPerformers": worst_performers,
                "bestSharpe": best_sharpe,
                "lowestRisk": lowest_risk,
                # Advanced metrics rankings
                "bestCalmar": best_calmar,
                "worstCalmar": worst_calmar,
                "bestSortino": best_sortino,
                "worstSortino": worst_sortino,
                "bestMaxDrawdown": best_max_drawdown,
                "worstMaxDrawdown": worst_max_drawdown,
                "bestUlcer": best_ulcer,
                "worstUlcer": worst_ulcer,
                "bestTimeUnderWater": best_time_under_water,
                "worstTimeUnderWater": worst_time_under_water,
                "bestCvar": best_cvar,
                "worstCvar": worst_cvar,
                "bestCorrelation": best_correlation,
                "worstCorrelation": worst_correlation,
                "bestRiskContribution": best_risk_contribution,
                "worstRiskContribution": worst_risk_contribution
            },
            "warnings": {
                "missingTickers": [],
                "tickersWithoutStartData": [],
                "firstAvailableDates": {}
            }
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticker comparison failed: {str(e)}")

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
