from dataclasses import dataclass
from typing import Optional
from ..interfaces.repositories import PortfolioRepository
from ...domain.entities.portfolio import Portfolio
from ...infrastructure.logging.logger_service import get_logger_service
from ...infrastructure.logging.decorators import log_operation

@dataclass
class LoadPortfolioRequest:
    file_path: str

@dataclass 
class LoadPortfolioResponse:
    portfolio: Optional[Portfolio]
    success: bool
    message: str

class LoadPortfolioUseCase:
    def __init__(self, portfolio_repo: PortfolioRepository):
        self._portfolio_repo = portfolio_repo
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("application")
    
    @log_operation("load_portfolio", include_args=True, include_result=True)
    def execute(self, request: LoadPortfolioRequest) -> LoadPortfolioResponse:
        self._logger.info(f"Starting portfolio load from: {request.file_path}")
        
        try:
            # Log file operation
            self._logger_service.log_file_operation("load", request.file_path, True, {"operation": "portfolio_load"})
            
            portfolio = self._portfolio_repo.load(request.file_path)
            
            # Log success
            ticker_count = len(portfolio.get_tickers())
            ticker_symbols = [t.symbol for t in portfolio.get_tickers()]
            
            self._logger.info(f"Portfolio loaded successfully: {ticker_count} positions")
            self._logger.debug(f"Loaded tickers: {', '.join(ticker_symbols)}")
            
            self._logger_service.log_business_operation(
                "load_portfolio", 
                "application", 
                True, 
                {
                    "file_path": request.file_path,
                    "ticker_count": ticker_count,
                    "tickers": ticker_symbols
                }
            )
            
            return LoadPortfolioResponse(
                portfolio=portfolio,
                success=True,
                message=f"Successfully loaded {ticker_count} positions"
            )
        except Exception as e:
            self._logger.error(f"Portfolio load failed: {str(e)}")
            self._logger_service.log_file_operation("load", request.file_path, False, {"error": str(e)})
            self._logger_service.log_business_operation(
                "load_portfolio", 
                "application", 
                False, 
                {"file_path": request.file_path, "error": str(e)}
            )
            
            return LoadPortfolioResponse(
                portfolio=None,
                success=False,
                message=f"Failed to load portfolio: {str(e)}"
            )
