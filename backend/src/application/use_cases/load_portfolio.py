from dataclasses import dataclass
from typing import Optional
from ..interfaces.repositories import PortfolioRepository
from ...domain.entities.portfolio import Portfolio

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
    
    def execute(self, request: LoadPortfolioRequest) -> LoadPortfolioResponse:
        try:
            portfolio = self._portfolio_repo.load(request.file_path)
            
            ticker_count = len(portfolio.get_tickers())
            
            return LoadPortfolioResponse(
                portfolio=portfolio,
                success=True,
                message=f"Successfully loaded {ticker_count} positions"
            )
        except Exception as e:
            return LoadPortfolioResponse(
                portfolio=None,
                success=False,
                message=f"Failed to load portfolio: {str(e)}"
            )
