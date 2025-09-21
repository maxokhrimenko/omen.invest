#!/usr/bin/env python3
"""
FastAPI wrapper for Portfolio Analysis Tool
Provides REST API endpoints for frontend integration
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.presentation.controllers.portfolio_controller import PortfolioController
from src.infrastructure.repositories.csv_portfolio_repository import CsvPortfolioRepository
from src.infrastructure.repositories.warehouse_market_repository import WarehouseMarketRepository
from src.infrastructure.config.warehouse_config import WarehouseConfig
from src.application.use_cases.load_portfolio import LoadPortfolioUseCase
from src.application.use_cases.analyze_portfolio import AnalyzePortfolioUseCase
from src.application.use_cases.analyze_ticker import AnalyzeTickerUseCase
from src.application.use_cases.compare_tickers import CompareTickersUseCase
from src.infrastructure.color_metrics_service import ColorMetricsService
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.position import Position

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for dependency injection
_controller: Optional[PortfolioController] = None
_current_portfolio: Optional[Portfolio] = None

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
    return _current_portfolio

def set_current_portfolio(portfolio: Optional[Portfolio]) -> None:
    """Set current portfolio."""
    global _current_portfolio
    _current_portfolio = portfolio

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.post("/portfolio/upload")
async def upload_portfolio(file: UploadFile = File(...)):
    """Upload portfolio CSV file."""
    try:
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
        from src.application.use_cases.load_portfolio import LoadPortfolioRequest
        
        request = LoadPortfolioRequest(file_path=temp_file_path)
        response = controller._load_portfolio_use_case.execute(request)
        
        if response.success and response.portfolio:
            set_current_portfolio(response.portfolio)
            
            # Convert to response format
            positions = [
                PositionResponse(ticker=pos.ticker.symbol, position=pos.position)
                for pos in response.portfolio.positions
            ]
            
            portfolio_response = PortfolioResponse(
                positions=positions,
                totalPositions=len(response.portfolio.positions),
                tickers=[t.symbol for t in response.portfolio.get_tickers()]
            )
            
            return ApiResponse(
                success=True,
                message=response.message,
                data=portfolio_response.dict()
            )
        else:
            raise HTTPException(status_code=400, detail=response.message)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/portfolio")
async def get_portfolio():
    """Get current portfolio."""
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # Convert to response format
    positions = [
        PositionResponse(ticker=pos.ticker.symbol, position=pos.position)
        for pos in portfolio.positions
    ]
    
    portfolio_response = PortfolioResponse(
        positions=positions,
        totalPositions=len(portfolio.positions),
        tickers=[t.symbol for t in portfolio.get_tickers()]
    )
    
    return portfolio_response

@app.delete("/portfolio")
async def clear_portfolio():
    """Clear current portfolio."""
    set_current_portfolio(None)
    return ApiResponse(success=True, message="Portfolio cleared successfully")

@app.get("/portfolio/analysis")
async def analyze_portfolio():
    """Analyze current portfolio."""
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # For now, return a placeholder response
    # TODO: Implement actual portfolio analysis
    return {
        "success": True,
        "message": "Portfolio analysis completed",
        "data": {
            "startValue": "$100,000",
            "endValue": "$105,000",
            "totalReturn": "5.0%",
            "annualizedReturn": "5.0%",
            "volatility": "12.5%",
            "sharpeRatio": "0.4",
            "maxDrawdown": "-8.2%"
        }
    }

@app.get("/portfolio/tickers/analysis")
async def analyze_tickers():
    """Analyze individual tickers in portfolio."""
    portfolio = get_current_portfolio()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio loaded")
    
    # For now, return a placeholder response
    # TODO: Implement actual ticker analysis
    return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
