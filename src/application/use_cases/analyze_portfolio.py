from dataclasses import dataclass
from typing import Optional, Dict, List
import pandas as pd
import numpy as np
from ..interfaces.repositories import MarketDataRepository
from ...domain.entities.portfolio import Portfolio
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...domain.value_objects.money import Money
from ...domain.value_objects.percentage import Percentage
from ...infrastructure.logging.logger_service import get_logger_service
from ...infrastructure.logging.decorators import log_operation, log_calculation

@dataclass
class AnalyzePortfolioRequest:
    portfolio: Portfolio
    date_range: DateRange
    risk_free_rate: float = 0.03

@dataclass
class PortfolioMetrics:
    total_return: Percentage
    annualized_return: Percentage
    volatility: Percentage
    sharpe_ratio: float
    max_drawdown: Percentage
    sortino_ratio: float
    calmar_ratio: float
    var_95: Percentage
    beta: float
    start_value: Money
    end_value: Money
    end_value_analysis: Money  # Only tickers with complete data
    end_value_missing: Money   # Only tickers missing data at start

@dataclass
class AnalyzePortfolioResponse:
    metrics: Optional[PortfolioMetrics]
    success: bool
    message: str
    missing_tickers: List[str] = None
    tickers_without_start_data: List[str] = None

class AnalyzePortfolioUseCase:
    def __init__(self, market_data_repo: MarketDataRepository):
        self._market_data_repo = market_data_repo
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("application")
    
    @log_operation("analyze_portfolio", include_args=True, include_result=True)
    def execute(self, request: AnalyzePortfolioRequest) -> AnalyzePortfolioResponse:
        ticker_symbols = [t.symbol for t in request.portfolio.get_tickers()]
        self._logger.info(f"Starting portfolio analysis for {len(ticker_symbols)} tickers: {', '.join(ticker_symbols)}")
        self._logger.info(f"Date range: {request.date_range.start} to {request.date_range.end}")
        
        try:
            # Get price history for all tickers
            self._logger.debug("Fetching price history from market data repository")
            price_history = self._market_data_repo.get_price_history(
                request.portfolio.get_tickers(),
                request.date_range
            )
            
            # Identify missing tickers and tickers without start data
            missing_tickers, tickers_without_start_data = self._identify_data_issues(
                request.portfolio.get_tickers(), 
                price_history, 
                request.date_range.start
            )
            
            if not price_history:
                self._logger.warning("No price data available for portfolio analysis")
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message="No price data available for portfolio analysis",
                    missing_tickers=missing_tickers,
                    tickers_without_start_data=tickers_without_start_data
                )
            
            self._logger.info(f"Retrieved price data for {len(price_history)} tickers")
            if missing_tickers:
                self._logger.warning(f"Missing data for tickers: {', '.join(missing_tickers)}")
            if tickers_without_start_data:
                self._logger.warning(f"Tickers without data at start date: {', '.join(tickers_without_start_data)}")
            
            # Calculate portfolio value over time
            self._logger.debug("Calculating portfolio values over time")
            portfolio_values, portfolio_values_analysis, portfolio_values_missing = self._calculate_portfolio_values(
                request.portfolio, price_history, tickers_without_start_data
            )
            
            if portfolio_values.empty:
                self._logger.error("Unable to calculate portfolio values")
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message="Unable to calculate portfolio values"
                )
            
            self._logger.info(f"Portfolio values calculated for {len(portfolio_values)} data points")
            
            # Check if we have valid data for analysis
            if portfolio_values_analysis.empty and portfolio_values.empty:
                self._logger.warning("No valid portfolio data available for analysis")
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message="No valid portfolio data available for analysis",
                    missing_tickers=missing_tickers,
                    tickers_without_start_data=tickers_without_start_data
                )
            
            # If we have data but no complete data for analysis, use total data but warn user
            if (portfolio_values_analysis.empty or portfolio_values_analysis.sum() == 0) and not portfolio_values.empty:
                self._logger.warning("No complete data available for analysis - using all available data")
                portfolio_values_analysis = portfolio_values
                # Also update the missing data to be empty since we're using all data
                portfolio_values_missing = pd.Series(dtype=float)
            
            # Calculate metrics using only complete data tickers
            self._logger.debug("Calculating portfolio metrics")
            try:
                metrics = self._calculate_metrics(
                    portfolio_values_analysis,  # Use only complete data for metrics
                    portfolio_values,           # Total portfolio values for display
                    portfolio_values_missing,   # Missing data values for display
                    request.risk_free_rate
                )
            except ValueError as e:
                self._logger.error(f"Portfolio metrics calculation failed: {str(e)}")
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message=f"Portfolio metrics calculation failed: {str(e)}",
                    missing_tickers=missing_tickers,
                    tickers_without_start_data=tickers_without_start_data
                )
            
            self._logger.info("Portfolio analysis completed successfully")
            self._logger.debug(f"Portfolio metrics: Total Return: {metrics.total_return}, Sharpe: {metrics.sharpe_ratio:.2f}")
            
            self._logger_service.log_business_operation(
                "analyze_portfolio",
                "application",
                True,
                {
                    "ticker_count": len(ticker_symbols),
                    "tickers": ticker_symbols,
                    "date_range": f"{request.date_range.start} to {request.date_range.end}",
                    "data_points": len(portfolio_values),
                    "total_return": str(metrics.total_return),
                    "sharpe_ratio": metrics.sharpe_ratio
                }
            )
            
            return AnalyzePortfolioResponse(
                metrics=metrics,
                success=True,
                message="Portfolio analysis completed successfully",
                missing_tickers=missing_tickers,
                tickers_without_start_data=tickers_without_start_data
            )
            
        except Exception as e:
            self._logger.error(f"Portfolio analysis failed: {str(e)}")
            self._logger_service.log_business_operation(
                "analyze_portfolio",
                "application",
                False,
                {
                    "ticker_count": len(ticker_symbols),
                    "tickers": ticker_symbols,
                    "error": str(e)
                }
            )
            
            return AnalyzePortfolioResponse(
                metrics=None,
                success=False,
                message=f"Portfolio analysis failed: {str(e)}"
            )
    
    def _calculate_portfolio_values(self, 
                                   portfolio: Portfolio, 
                                   price_history: Dict[Ticker, pd.Series],
                                   tickers_without_start_data: List[str]) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate portfolio value over time, separating complete and incomplete data tickers."""
        # Align all price series by date
        price_df = pd.DataFrame(price_history)
        if price_df.empty:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        
        # Calculate position values for all tickers
        portfolio_values = pd.Series(0.0, index=price_df.index)
        # Calculate position values for complete data tickers only
        portfolio_values_analysis = pd.Series(0.0, index=price_df.index)
        # Calculate position values for incomplete data tickers only
        portfolio_values_missing = pd.Series(0.0, index=price_df.index)
        
        for position in portfolio:
            if position.ticker in price_history:
                ticker_prices = price_history[position.ticker]
                position_values = ticker_prices * float(position.quantity)
                portfolio_values = portfolio_values.add(position_values, fill_value=0)
                
                # Separate based on whether ticker has complete data
                if position.ticker.symbol in tickers_without_start_data:
                    portfolio_values_missing = portfolio_values_missing.add(position_values, fill_value=0)
                else:
                    portfolio_values_analysis = portfolio_values_analysis.add(position_values, fill_value=0)
        
        return portfolio_values.dropna(), portfolio_values_analysis.dropna(), portfolio_values_missing.dropna()
    
    def _identify_data_issues(self, 
                             tickers: List[Ticker], 
                             price_history: Dict[Ticker, pd.Series], 
                             start_date: str) -> tuple[List[str], List[str]]:
        """Identify tickers with missing data or no data at start date."""
        missing_tickers = []
        tickers_without_start_data = []
        
        start_timestamp = pd.Timestamp(start_date)
        # Allow up to 5 business days tolerance for start date (to account for weekends/holidays)
        tolerance_days = 5
        max_allowed_start = start_timestamp + pd.Timedelta(days=tolerance_days)
        
        for ticker in tickers:
            if ticker not in price_history:
                missing_tickers.append(ticker.symbol)
                self._logger.warning(f"No price data available for {ticker.symbol}")
            else:
                prices = price_history[ticker]
                if prices.empty:
                    missing_tickers.append(ticker.symbol)
                    self._logger.warning(f"Empty price data for {ticker.symbol}")
                else:
                    # Check if there's data within reasonable tolerance of the start date
                    available_dates = prices.index
                    first_available = available_dates[0]
                    
                    # If first available data is more than tolerance_days after start date, consider it missing
                    if first_available > max_allowed_start:
                        tickers_without_start_data.append(ticker.symbol)
                        self._logger.warning(f"No data within {tolerance_days} days of start date {start_date} for {ticker.symbol} (first data: {first_available.date()})")
                    else:
                        self._logger.debug(f"Data available for {ticker.symbol} within tolerance (first data: {first_available.date()})")
        
        return missing_tickers, tickers_without_start_data
    
    @log_calculation("portfolio_metrics", include_inputs=True, include_outputs=True)
    def _calculate_metrics(self, 
                          portfolio_values_analysis: pd.Series,  # Only complete data for calculations
                          portfolio_values_total: pd.Series,     # Total values for display
                          portfolio_values_missing: pd.Series,   # Missing data values for display
                          risk_free_rate: float) -> PortfolioMetrics:
        """Calculate portfolio performance metrics using only complete data tickers."""
        self._logger.debug(f"Calculating portfolio metrics for {len(portfolio_values_analysis)} data points")
        
        # Use only complete data for all calculations
        if portfolio_values_analysis.empty:
            # Fallback to total values if no complete data
            portfolio_values_analysis = portfolio_values_total
        
        # Ensure we have data to work with
        if portfolio_values_analysis.empty:
            raise ValueError("No portfolio data available for metrics calculation")
        
        # Calculate returns using only complete data
        returns = portfolio_values_analysis.pct_change().dropna()
        
        # Basic metrics using complete data
        start_value = Money(portfolio_values_analysis.iloc[0])
        end_value_analysis = Money(portfolio_values_analysis.iloc[-1])
        
        # Check for division by zero
        if start_value.amount == 0:
            raise ValueError("Portfolio start value is zero - cannot calculate returns")
        
        total_return = Percentage(float((end_value_analysis.amount - start_value.amount) / start_value.amount) * 100)
        
        # Calculate separate end values for display
        end_value_total = Money(portfolio_values_total.iloc[-1]) if not portfolio_values_total.empty else Money(0)
        end_value_missing = Money(portfolio_values_missing.iloc[-1]) if not portfolio_values_missing.empty else Money(0)
        
        # Annualized return
        days = len(returns)
        if days > 0:
            total_return_ratio = float(end_value_analysis.amount / start_value.amount)
            annualized_return = Percentage(
                (total_return_ratio ** (252 / days) - 1) * 100
            )
        else:
            annualized_return = Percentage(0)
        
        # Risk metrics
        volatility = Percentage(returns.std() * np.sqrt(252) * 100)
        
        # Sharpe ratio
        rf_daily = risk_free_rate / 252
        excess_returns = returns - rf_daily
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0
        
        # Max drawdown
        cumulative_returns = (1 + returns).cumprod()
        max_drawdown = Percentage(
            ((cumulative_returns - cumulative_returns.cummax()) / cumulative_returns.cummax()).min() * 100
        )
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        sortino_ratio = (
            np.sqrt(252) * excess_returns.mean() / downside_returns.std() 
            if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
        )
        
        # Calmar ratio
        calmar_ratio = (
            float(annualized_return.value) / abs(float(max_drawdown.value)) 
            if float(max_drawdown.value) != 0 else 0
        )
        
        # VaR (95%)
        var_95 = Percentage(np.percentile(returns, 5) * 100)
        
        # Beta (placeholder - would need benchmark data)
        beta = 1.0
        
        return PortfolioMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            var_95=var_95,
            beta=beta,
            start_value=start_value,
            end_value=end_value_total,  # Total end value for display
            end_value_analysis=end_value_analysis,  # Only complete data
            end_value_missing=end_value_missing  # Only missing data
        )
