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
    first_available_dates: Optional[Dict[str, str]] = None
    portfolio_values_over_time: Optional[Dict[str, float]] = None
    sp500_values_over_time: Optional[Dict[str, float]] = None
    nasdaq_values_over_time: Optional[Dict[str, float]] = None

class AnalyzePortfolioUseCase:
    def __init__(self, market_data_repo: MarketDataRepository):
        self._market_data_repo = market_data_repo
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("application")
    
    @log_operation("analyze_portfolio", include_args=True, include_result=True)
    def execute(self, request: AnalyzePortfolioRequest) -> AnalyzePortfolioResponse:
        ticker_symbols = [t.symbol for t in request.portfolio.get_tickers()]
        self._logger.info(
            f"Starting portfolio analysis for {len(ticker_symbols)} tickers: "
            f"{', '.join(ticker_symbols)}"
        )
        self._logger.info(f"Date range: {request.date_range.start} to {request.date_range.end}")
        
        # Add warning for large portfolios
        if len(ticker_symbols) > 100:
            self._logger.warning(f"Large portfolio detected ({len(ticker_symbols)} tickers). Analysis may take longer.")
        
        try:
            # Get price history for all tickers
            self._logger.debug("Fetching price history from market data repository")
            price_history = self._market_data_repo.get_price_history(
                request.portfolio.get_tickers(),
                request.date_range
            )
            
            # Identify missing tickers and tickers without start data
            missing_tickers, tickers_without_start_data, first_available_dates = self._identify_data_issues(
                request.portfolio.get_tickers(), 
                price_history, 
                request.date_range.start,
                request.date_range.end
            )
            
            if not price_history:
                self._logger.warning("No price data available for portfolio analysis")
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message="No price data available for portfolio analysis",
                    missing_tickers=missing_tickers,
                    tickers_without_start_data=tickers_without_start_data,
                    first_available_dates=first_available_dates,
                    portfolio_values_over_time={},
                    sp500_values_over_time={},
                    nasdaq_values_over_time={}
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
                    message="Unable to calculate portfolio values",
                    missing_tickers=[],
                    tickers_without_start_data=[],
                    first_available_dates={},
                    portfolio_values_over_time={},
                    sp500_values_over_time={},
                    nasdaq_values_over_time={}
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
                    tickers_without_start_data=tickers_without_start_data,
                    first_available_dates=first_available_dates,
                    portfolio_values_over_time={},
                    sp500_values_over_time={},
                    nasdaq_values_over_time={}
                )
            
            # If we have data but no complete data for analysis, use total data but warn user
            if (portfolio_values_analysis.empty or portfolio_values_analysis.sum() == 0) and not portfolio_values.empty:
                self._logger.warning("No complete data available for analysis - using all available data")
                portfolio_values_analysis = portfolio_values
                # Also update the missing data to be empty since we're using all data
                portfolio_values_missing = pd.Series(dtype=float)
            
            # Get benchmark data for Beta calculation
            self._logger.debug("Fetching benchmark data for Beta calculation")
            benchmark_data = self._market_data_repo.get_benchmark_data(
                "^GSPC",  # S&P 500 symbol
                request.date_range
            )
            
            # Get NASDAQ data for chart comparison
            self._logger.debug("Fetching NASDAQ data for chart comparison")
            nasdaq_data = self._market_data_repo.get_benchmark_data(
                "^IXIC",  # NASDAQ Composite symbol
                request.date_range
            )
            
            # Calculate metrics using only complete data tickers
            self._logger.debug("Calculating portfolio metrics")
            try:
                metrics = self._calculate_metrics(
                    portfolio_values_analysis,  # Use only complete data for metrics
                    portfolio_values,           # Total portfolio values for display
                    portfolio_values_missing,   # Missing data values for display
                    request.risk_free_rate,
                    request.portfolio,          # Portfolio for Beta calculation
                    price_history,             # Price history for Beta calculation
                    benchmark_data,            # Benchmark data for Beta calculation
                    request.date_range         # Date range for Beta calculation
                )
            except ValueError as e:
                self._logger.error(f"Portfolio metrics calculation failed: {str(e)}")
                return AnalyzePortfolioResponse(
                    metrics=None,
                    success=False,
                    message=f"Portfolio metrics calculation failed: {str(e)}",
                    missing_tickers=missing_tickers,
                    tickers_without_start_data=tickers_without_start_data,
                    portfolio_values_over_time={},
                    sp500_values_over_time={},
                    nasdaq_values_over_time={}
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
            
            # Convert time series data to dictionaries for API response
            portfolio_values_dict = {}
            sp500_values_dict = {}
            nasdaq_values_dict = {}
            
            if not portfolio_values_analysis.empty:
                portfolio_values_dict = {
                    date.strftime('%Y-%m-%d'): float(value) 
                    for date, value in portfolio_values_analysis.items()
                }
            
            if not benchmark_data.empty:
                sp500_values_dict = {
                    date.strftime('%Y-%m-%d'): float(value) 
                    for date, value in benchmark_data.items()
                }
            
            if not nasdaq_data.empty:
                nasdaq_values_dict = {
                    date.strftime('%Y-%m-%d'): float(value) 
                    for date, value in nasdaq_data.items()
                }
            
            return AnalyzePortfolioResponse(
                metrics=metrics,
                success=True,
                message="Portfolio analysis completed successfully",
                missing_tickers=missing_tickers,
                tickers_without_start_data=tickers_without_start_data,
                first_available_dates=first_available_dates,
                portfolio_values_over_time=portfolio_values_dict,
                sp500_values_over_time=sp500_values_dict,
                nasdaq_values_over_time=nasdaq_values_dict
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
                message=f"Portfolio analysis failed: {str(e)}",
                missing_tickers=[],
                tickers_without_start_data=[],
                first_available_dates={},
                portfolio_values_over_time={},
                sp500_values_over_time={},
                nasdaq_values_over_time={}
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
                             start_date: str,
                             end_date: str = None) -> tuple[List[str], List[str], Dict[str, str]]:
        """Identify tickers with missing data or no data at start date."""
        missing_tickers = []
        tickers_without_start_data = []
        first_available_dates = {}
        
        start_timestamp = pd.Timestamp(start_date)
        end_timestamp = pd.Timestamp(end_date) if end_date else pd.Timestamp.now()
        
        # Calculate expected trading days for the actual date range
        # Approximate trading days: ~252 per year (weekdays minus holidays)
        date_range_days = (end_timestamp - start_timestamp).days
        estimated_trading_days = max(int(date_range_days * 0.7), 10)  # 70% of calendar days are trading days, minimum 10
        
        self._logger.debug(f"Date range: {start_date} to {end_date}, estimated trading days: {estimated_trading_days}")
        
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
                    first_available = prices.index[0]
                    
                    # Check if data starts after the requested start date (with business day tolerance)
                    # Allow up to 5 business days tolerance for start date (to account for weekends/holidays)
                    tolerance_days = 5
                    max_allowed_start = start_timestamp + pd.Timedelta(days=tolerance_days)
                    has_data_at_start = first_available <= max_allowed_start
                    
                    if not has_data_at_start:
                        tickers_without_start_data.append(ticker.symbol)
                        first_available_dates[ticker.symbol] = first_available.strftime('%Y-%m-%d')
                        days_late = (first_available - start_timestamp).days
                        self._logger.warning(f"Data starts after requested start date for {ticker.symbol}: {first_available.strftime('%Y-%m-%d')} (requested: {start_date}, {days_late} days late, tolerance: {tolerance_days} days)")
                    else:
                        # Additional check for extremely poor data coverage
                        # This catches cases where data exists but is insufficient for analysis
                        data_coverage_ratio = len(prices) / max(estimated_trading_days, 1)
                        
                        # More lenient threshold for shorter periods
                        min_data_points = max(10, int(estimated_trading_days * 0.1))  # At least 10% of expected trading days
                        coverage_threshold = 0.1 if estimated_trading_days > 100 else 0.05  # More lenient for shorter periods
                        
                        if len(prices) < min_data_points or data_coverage_ratio < coverage_threshold:
                            tickers_without_start_data.append(ticker.symbol)
                            first_available_dates[ticker.symbol] = first_available.strftime('%Y-%m-%d')
                            self._logger.warning(f"Insufficient data coverage for {ticker.symbol}: {len(prices)} data points, coverage ratio: {data_coverage_ratio:.2%} (expected: {estimated_trading_days}, threshold: {coverage_threshold:.1%})")
                        else:
                            self._logger.debug(f"Sufficient data for {ticker.symbol}: starts {first_available.strftime('%Y-%m-%d')}, {len(prices)} data points, coverage ratio: {data_coverage_ratio:.2%}")
        
        return missing_tickers, tickers_without_start_data, first_available_dates
    
    def _calculate_var_95(self, returns: pd.Series) -> Percentage:
        """Calculate VaR 95% with proper validation and error handling."""
        if len(returns) < 5:
            # Insufficient data for reliable VaR calculation
            self._logger.warning(f"Insufficient data for VaR calculation: {len(returns)} observations")
            return Percentage(0)  # Default to 0 when insufficient data
        
        # Calculate VaR using historical simulation method
        var_95_raw = np.percentile(returns, 5) * 100
        
        # Validate VaR result - it should be negative (representing a loss)
        if var_95_raw > 0:
            self._logger.warning(f"VaR calculation resulted in positive value: {var_95_raw:.2f}%. This may indicate insufficient negative returns in the data.")
            
            # Check if we have any negative returns at all
            negative_returns = returns[returns < 0]
            if not negative_returns.empty:
                # Use the worst negative return as VaR
                var_95_raw = negative_returns.min() * 100
                self._logger.info(f"Using worst negative return as VaR: {var_95_raw:.2f}%")
            else:
                # No negative returns - this is very unusual for financial data
                # In this case, we cannot calculate a meaningful VaR, so we set it to 0
                # This indicates that there's no historical loss to base VaR on
                self._logger.warning("No negative returns found - setting VaR to 0% (no historical losses)")
                var_95_raw = 0
        
        # Additional validation: VaR should not be more extreme than the worst return
        # Only apply this validation if we have a meaningful VaR (negative)
        if var_95_raw < 0:
            worst_return = returns.min() * 100
            if var_95_raw < worst_return:
                self._logger.warning(f"VaR ({var_95_raw:.2f}%) is more extreme than worst return ({worst_return:.2f}%) - using worst return")
                var_95_raw = worst_return
        
        return Percentage(var_95_raw)
    
    def _calculate_portfolio_beta(self, portfolio: Portfolio, 
                                 price_history: Dict[Ticker, pd.Series],
                                 benchmark_data: pd.Series,
                                 date_range: DateRange) -> float:
        """Calculate portfolio Beta as weighted average of individual stock betas."""
        if benchmark_data is None or benchmark_data.empty:
            self._logger.warning("No benchmark data available for portfolio Beta calculation")
            return 1.0
        
        benchmark_returns = benchmark_data.pct_change().dropna()
        total_portfolio_value = 0
        weighted_beta_sum = 0
        
        for ticker in portfolio.get_tickers():
            if ticker not in price_history:
                self._logger.warning(f"No price data for {ticker.symbol} - skipping from Beta calculation")
                continue
            
            prices = price_history[ticker]
            if prices.empty or len(prices) < 2:
                self._logger.warning(f"Insufficient price data for {ticker.symbol} - skipping from Beta calculation")
                continue
            
            # Calculate position value (using current price)
            position = portfolio.get_position(ticker)
            if position is None:
                continue
            
            # Use the latest price for weighting
            current_price = Money(prices.iloc[-1])
            position_value = position.get_value(current_price)
            total_portfolio_value += float(position_value.amount)
            
            # Calculate individual stock beta
            returns = prices.pct_change().dropna()
            stock_beta = self._calculate_individual_beta(ticker, returns, benchmark_returns)
            weighted_beta_sum += stock_beta * float(position_value.amount)
        
        if total_portfolio_value == 0:
            self._logger.warning("Total portfolio value is zero - cannot calculate portfolio Beta")
            return 1.0
        
        portfolio_beta = weighted_beta_sum / total_portfolio_value
        self._logger.info(f"Calculated portfolio Beta: {portfolio_beta:.3f}")
        return portfolio_beta
    
    def _calculate_individual_beta(self, ticker: Ticker, returns: pd.Series, 
                                  benchmark_returns: pd.Series) -> float:
        """Calculate Beta for an individual ticker against benchmark."""
        if len(returns) < 5 or len(benchmark_returns) < 5:
            return 1.0  # Default to market beta
        
        # Align the data by date
        common_dates = returns.index.intersection(benchmark_returns.index)
        if len(common_dates) < 5:
            return 1.0
        
        aligned_returns = returns.loc[common_dates]
        aligned_benchmark = benchmark_returns.loc[common_dates]
        
        # Ensure data is 1D for covariance calculation
        if aligned_benchmark.ndim > 1:
            aligned_benchmark = aligned_benchmark.iloc[:, 0] if hasattr(aligned_benchmark, 'iloc') else aligned_benchmark.flatten()
        
        # Calculate covariance and variance
        covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
        benchmark_variance = np.var(aligned_benchmark)
        
        if benchmark_variance == 0:
            return 1.0
        
        beta = covariance / benchmark_variance
        
        # Validate Beta result
        if np.isnan(beta) or np.isinf(beta):
            return 1.0
        
        return beta
    
    @log_calculation("portfolio_metrics", include_inputs=True, include_outputs=True)
    def _calculate_metrics(self, 
                          portfolio_values_analysis: pd.Series,  # Only complete data for calculations
                          portfolio_values_total: pd.Series,     # Total values for display
                          portfolio_values_missing: pd.Series,   # Missing data values for display
                          risk_free_rate: float,
                          portfolio: Portfolio = None,           # Portfolio for Beta calculation
                          price_history: Dict[Ticker, pd.Series] = None,  # Price history for Beta calculation
                          benchmark_data: pd.Series = None,      # Benchmark data for Beta calculation
                          date_range: DateRange = None) -> PortfolioMetrics:
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
        start_value = Money(float(portfolio_values_analysis.iloc[0]))
        end_value_analysis = Money(float(portfolio_values_analysis.iloc[-1]))
        
        # Check for division by zero
        if start_value.amount == 0:
            raise ValueError("Portfolio start value is zero - cannot calculate returns")
        
        total_return = Percentage(float((end_value_analysis.amount - start_value.amount) / start_value.amount) * 100)
        
        # Calculate separate end values for display
        end_value_total = Money(float(portfolio_values_total.iloc[-1])) if not portfolio_values_total.empty else Money(0)
        end_value_missing = Money(float(portfolio_values_missing.iloc[-1])) if not portfolio_values_missing.empty else Money(0)
        
        # Annualized return
        days = len(returns)
        if not returns.empty:
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
        excess_std = excess_returns.std()
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_std if excess_std > 0 else 0
        
        # Max drawdown
        cumulative_returns = (1 + returns).cumprod()
        max_drawdown = Percentage(
            ((cumulative_returns - cumulative_returns.cummax()) / cumulative_returns.cummax()).min() * 100
        )
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if not downside_returns.empty else 0
        sortino_ratio = (
            np.sqrt(252) * excess_returns.mean() / downside_std 
            if downside_std > 0 else 0
        )
        
        # Calmar ratio
        calmar_ratio = (
            float(annualized_return.value) / abs(float(max_drawdown.value)) 
            if float(max_drawdown.value) != 0 else 0
        )
        
        # VaR (95%) - Historical simulation method with validation
        # For VaR 95%, we take the 5th percentile of returns (worst 5% of outcomes)
        # This represents the maximum expected loss with 95% confidence
        var_95 = self._calculate_var_95(returns)
        
        # Beta calculation against S&P 500
        if (portfolio is not None and price_history is not None and 
            benchmark_data is not None and hasattr(benchmark_data, 'empty') and not benchmark_data.empty and 
            date_range is not None):
            beta = self._calculate_portfolio_beta(portfolio, price_history, benchmark_data, date_range)
        else:
            self._logger.warning("Insufficient data for portfolio Beta calculation - using default value")
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
