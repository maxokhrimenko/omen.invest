from typing import Optional, List
from ...application.use_cases.load_portfolio import LoadPortfolioUseCase, LoadPortfolioRequest
from ...application.use_cases.analyze_portfolio import AnalyzePortfolioUseCase, AnalyzePortfolioRequest
from ...application.use_cases.analyze_ticker import AnalyzeTickerUseCase, AnalyzeTickerRequest
from ...application.use_cases.compare_tickers import CompareTickersUseCase, CompareTickersRequest
from ...domain.entities.portfolio import Portfolio
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...infrastructure.color_metrics_service import ColorMetricsService


class MainController:
    """Main controller for portfolio analysis operations."""
    
    def __init__(self, 
                 load_portfolio_use_case: LoadPortfolioUseCase,
                 analyze_portfolio_use_case: AnalyzePortfolioUseCase,
                 analyze_ticker_use_case: AnalyzeTickerUseCase,
                 compare_tickers_use_case: CompareTickersUseCase,
                 color_service: ColorMetricsService = None):
        self._load_portfolio_use_case = load_portfolio_use_case
        self._analyze_portfolio_use_case = analyze_portfolio_use_case
        self._analyze_ticker_use_case = analyze_ticker_use_case
        self._compare_tickers_use_case = compare_tickers_use_case
        self._color_service = color_service or ColorMetricsService()
        self._current_portfolio: Optional[Portfolio] = None
        self._default_start_date = "2024-03-01"
        self._risk_free_rate = 0.03
    
    @property
    def current_portfolio(self) -> Optional[Portfolio]:
        """Get the current portfolio."""
        return self._current_portfolio
    
    @current_portfolio.setter
    def current_portfolio(self, portfolio: Optional[Portfolio]) -> None:
        """Set the current portfolio."""
        self._current_portfolio = portfolio
    
    def load_portfolio(self, file_path: str) -> LoadPortfolioRequest:
        """Load portfolio from file."""
        request = LoadPortfolioRequest(file_path=file_path)
        response = self._load_portfolio_use_case.execute(request)
        
        if response.success and response.portfolio:
            self._current_portfolio = response.portfolio
        
        return response
    
    def analyze_portfolio(self, portfolio: Portfolio, date_range: DateRange, risk_free_rate: float = 0.03) -> AnalyzePortfolioRequest:
        """Analyze portfolio with given parameters."""
        request = AnalyzePortfolioRequest(
            portfolio=portfolio,
            date_range=date_range,
            risk_free_rate=risk_free_rate
        )
        
        return self._analyze_portfolio_use_case.execute(request)
    
    def analyze_ticker(self, ticker: Ticker, date_range: DateRange, risk_free_rate: float = 0.03) -> AnalyzeTickerRequest:
        """Analyze individual ticker."""
        request = AnalyzeTickerRequest(
            ticker=ticker,
            date_range=date_range,
            risk_free_rate=risk_free_rate
        )
        
        return self._analyze_ticker_use_case.execute(request)
    
    def analyze_tickers_batch(self, tickers: List[Ticker], date_range: DateRange, risk_free_rate: float = 0.03) -> AnalyzeTickerRequest:
        """Analyze multiple tickers in batch."""
        from ...application.use_cases.analyze_ticker import AnalyzeTickersRequest
        
        request = AnalyzeTickersRequest(
            tickers=tickers,
            date_range=date_range,
            risk_free_rate=risk_free_rate
        )
        
        return self._analyze_ticker_use_case.execute_batch(request)
    
    def compare_tickers(self, tickers: List[Ticker], date_range: DateRange, risk_free_rate: float = 0.03) -> CompareTickersRequest:
        """Compare tickers."""
        from ...application.use_cases.compare_tickers import CompareTickersRequest
        
        request = CompareTickersRequest(
            tickers=tickers,
            date_range=date_range,
            risk_free_rate=risk_free_rate
        )
        
        return self._compare_tickers_use_case.execute(request)
    