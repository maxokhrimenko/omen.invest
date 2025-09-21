from typing import Optional, List
from datetime import date
from ...application.use_cases.load_portfolio import LoadPortfolioUseCase, LoadPortfolioRequest
from ...application.use_cases.analyze_portfolio import AnalyzePortfolioUseCase, AnalyzePortfolioRequest
from ...application.use_cases.analyze_ticker import AnalyzeTickerUseCase, AnalyzeTickerRequest
from ...application.use_cases.compare_tickers import CompareTickersUseCase, CompareTickersRequest
from ...domain.entities.portfolio import Portfolio
from ...domain.entities.ticker import Ticker
from ...domain.value_objects.date_range import DateRange
from ...infrastructure.logging.logger_service import get_logger_service
from ...infrastructure.logging.decorators import log_user_action

class PortfolioController:
    def __init__(self, 
                 load_portfolio_use_case: LoadPortfolioUseCase,
                 analyze_portfolio_use_case: AnalyzePortfolioUseCase,
                 analyze_ticker_use_case: AnalyzeTickerUseCase,
                 compare_tickers_use_case: CompareTickersUseCase):
        self._load_portfolio_use_case = load_portfolio_use_case
        self._analyze_portfolio_use_case = analyze_portfolio_use_case
        self._analyze_ticker_use_case = analyze_ticker_use_case
        self._compare_tickers_use_case = compare_tickers_use_case
        self._current_portfolio: Optional[Portfolio] = None
        self._default_start_date = "2024-03-01"
        self._risk_free_rate = 0.03
        
        # Initialize logging
        self._logger_service = get_logger_service()
        self._logger = self._logger_service.get_logger("presentation")
        self._logger.info("PortfolioController initialized")
    
    @log_user_action("load_portfolio", include_inputs=True)
    def load_portfolio(self) -> None:
        """Load portfolio from file."""
        self._logger.info("User initiated portfolio load")
        print("\n📁 Load Portfolio")
        print("─" * 50)
        
        file_path = input("Enter portfolio file path (default: input/input.csv): ").strip()
        if not file_path:
            file_path = "input/input.csv"
        
        self._logger.info(f"User selected file path: {file_path}")
        self._logger_service.log_user_action("load_portfolio", {"file_path": file_path})
        
        request = LoadPortfolioRequest(file_path=file_path)
        response = self._load_portfolio_use_case.execute(request)
        
        if response.success:
            self._current_portfolio = response.portfolio
            self._logger.info(f"Portfolio loaded successfully: {response.message}")
            print(f"✅ {response.message}")
            self._display_portfolio_summary()
        else:
            self._logger.error(f"Portfolio load failed: {response.message}")
            print(f"❌ {response.message}")
    
    def analyze_portfolio(self) -> None:
        """Analyze current portfolio."""
        if not self._current_portfolio:
            print("❌ No portfolio loaded. Please load a portfolio first.")
            return
        
        print("\n📊 Portfolio Analysis")
        print("─" * 50)
        
        date_range = self._get_date_range()
        
        request = AnalyzePortfolioRequest(
            portfolio=self._current_portfolio,
            date_range=date_range,
            risk_free_rate=self._risk_free_rate
        )
        
        print("🔄 Analyzing portfolio...")
        response = self._analyze_portfolio_use_case.execute(request)
        
        if response.success and response.metrics:
            self._display_portfolio_metrics(response.metrics)
            self._display_data_issues(response.missing_tickers, response.tickers_without_start_data)
        else:
            print(f"❌ {response.message}")
            if hasattr(response, 'missing_tickers') or hasattr(response, 'tickers_without_start_data'):
                self._display_data_issues(
                    getattr(response, 'missing_tickers', []), 
                    getattr(response, 'tickers_without_start_data', [])
                )
    
    def analyze_tickers(self) -> None:
        """Analyze individual tickers in portfolio."""
        if not self._current_portfolio:
            print("❌ No portfolio loaded. Please load a portfolio first.")
            return
        
        print("\n📈 Ticker Analysis")
        print("─" * 50)
        
        # Show available tickers
        tickers = self._current_portfolio.get_tickers()
        print("Available tickers:")
        for i, ticker in enumerate(tickers, 1):
            print(f"{i:2d}. {ticker.symbol}")
        
        print("\nOptions:")
        print("1. Analyze all tickers")
        print("2. Analyze specific ticker")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            self._analyze_all_tickers()
        elif choice == "2":
            self._analyze_specific_ticker()
        else:
            print("❌ Invalid choice.")
    
    def compare_tickers(self) -> None:
        """Compare tickers in portfolio."""
        if not self._current_portfolio:
            print("❌ No portfolio loaded. Please load a portfolio first.")
            return
        
        print("\n🔬 Ticker Comparison")
        print("─" * 50)
        
        tickers = self._current_portfolio.get_tickers()
        if len(tickers) < 2:
            print("❌ Need at least 2 tickers for comparison.")
            return
        
        date_range = self._get_date_range()
        
        request = CompareTickersRequest(
            tickers=tickers,
            date_range=date_range,
            risk_free_rate=self._risk_free_rate
        )
        
        print("🔄 Comparing tickers...")
        response = self._compare_tickers_use_case.execute(request)
        
        if response.success and response.comparison:
            self._display_ticker_comparison(response.comparison)
        else:
            print(f"❌ {response.message}")
    
    def generate_report(self) -> None:
        """Generate comprehensive report."""
        if not self._current_portfolio:
            print("❌ No portfolio loaded. Please load a portfolio first.")
            return
        
        print("\n📋 Generating Comprehensive Report")
        print("─" * 50)
        
        # Run portfolio analysis
        print("🔄 Running portfolio analysis...")
        self.analyze_portfolio()
        
        print("\n")
        # Run ticker comparison
        print("🔄 Running ticker comparison...")
        self.compare_tickers()
    
    def show_settings(self) -> None:
        """Show and modify settings."""
        print("\n⚙️ Settings")
        print("─" * 50)
        print(f"Default start date: {self._default_start_date}")
        print(f"Risk-free rate: {self._risk_free_rate:.1%}")
        
        print("\nOptions:")
        print("1. Change default start date")
        print("2. Change risk-free rate")
        print("3. Back to main menu")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            new_date = input(f"Enter new start date (YYYY-MM-DD, current: {self._default_start_date}): ").strip()
            if new_date:
                try:
                    # Validate date format
                    date.fromisoformat(new_date)
                    self._default_start_date = new_date
                    print(f"✅ Start date updated to {new_date}")
                except ValueError:
                    print("❌ Invalid date format. Please use YYYY-MM-DD.")
        elif choice == "2":
            new_rate = input(f"Enter new risk-free rate (decimal, current: {self._risk_free_rate}): ").strip()
            if new_rate:
                try:
                    rate = float(new_rate)
                    if 0 <= rate <= 1:
                        self._risk_free_rate = rate
                        print(f"✅ Risk-free rate updated to {rate:.1%}")
                    else:
                        print("❌ Risk-free rate must be between 0 and 1.")
                except ValueError:
                    print("❌ Invalid number format.")
    
    def _get_date_range(self) -> DateRange:
        """Get date range from user input."""
        start_date = input(f"Enter start date (YYYY-MM-DD, default: {self._default_start_date}): ").strip()
        if not start_date:
            start_date = self._default_start_date
        
        end_date = input("Enter end date (YYYY-MM-DD, default: today): ").strip()
        if not end_date:
            end_date = date.today().isoformat()
        
        return DateRange(start_date, end_date)
    
    def _display_portfolio_summary(self) -> None:
        """Display portfolio summary."""
        if not self._current_portfolio:
            return
        
        print(f"\nPortfolio Summary:")
        print(f"Total positions: {len(self._current_portfolio)}")
        print("Tickers:", ", ".join([t.symbol for t in self._current_portfolio.get_tickers()]))
    
    def _display_portfolio_metrics(self, metrics) -> None:
        """Display portfolio analysis results."""
        print("\n📊 PORTFOLIO ANALYSIS RESULTS")
        print("=" * 60)
        print(f"💸 Start Value:       {metrics.start_value}")
        print(f"💰 End Value:         {metrics.end_value}")
        print(f"🔺 Total Return:      {metrics.total_return}")
        print(f"📈 Annualized Return: {metrics.annualized_return}")
        print(f"📊 Volatility:        {metrics.volatility}")
        print(f"📏 Sharpe Ratio:      {metrics.sharpe_ratio:.2f}")
        print(f"📉 Max Drawdown:      {metrics.max_drawdown}")
        print(f"📈 Sortino Ratio:     {metrics.sortino_ratio:.2f}")
        print(f"📊 Calmar Ratio:      {metrics.calmar_ratio:.2f}")
        print(f"⚠️  VaR (95%):        {metrics.var_95}")
        print(f"β  Beta:             {metrics.beta:.2f}")
        print("=" * 60)
    
    def _analyze_all_tickers(self) -> None:
        """Analyze all tickers in portfolio."""
        date_range = self._get_date_range()
        
        print("🔄 Analyzing all tickers...")
        results = []
        
        for ticker in self._current_portfolio.get_tickers():
            request = AnalyzeTickerRequest(
                ticker=ticker,
                date_range=date_range,
                risk_free_rate=self._risk_free_rate
            )
            
            response = self._analyze_ticker_use_case.execute(request)
            if response.success and response.metrics:
                results.append(response.metrics)
            else:
                if not response.has_data_at_start and response.first_available_date:
                    print(f"⚠️  {ticker.symbol}: No data at start date. First available: {response.first_available_date}")
                else:
                    print(f"⚠️  Failed to analyze {ticker.symbol}: {response.message}")
        
        if results:
            self._display_ticker_results(results)
    
    def _analyze_specific_ticker(self) -> None:
        """Analyze a specific ticker."""
        tickers = self._current_portfolio.get_tickers()
        
        print("Select ticker to analyze:")
        for i, ticker in enumerate(tickers, 1):
            print(f"{i:2d}. {ticker.symbol}")
        
        try:
            choice = int(input("\nEnter ticker number: ").strip())
            if 1 <= choice <= len(tickers):
                selected_ticker = tickers[choice - 1]
                date_range = self._get_date_range()
                
                request = AnalyzeTickerRequest(
                    ticker=selected_ticker,
                    date_range=date_range,
                    risk_free_rate=self._risk_free_rate
                )
                
                print(f"🔄 Analyzing {selected_ticker.symbol}...")
                response = self._analyze_ticker_use_case.execute(request)
                
                if response.success and response.metrics:
                    self._display_ticker_results([response.metrics])
                else:
                    if not response.has_data_at_start and response.first_available_date:
                        print(f"❌ {selected_ticker.symbol}: No data at start date. First available: {response.first_available_date}")
                    else:
                        print(f"❌ {response.message}")
            else:
                print("❌ Invalid ticker number.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    def _display_ticker_results(self, results) -> None:
        """Display ticker analysis results."""
        print(f"\n📈 TICKER ANALYSIS RESULTS ({len(results)} tickers)")
        print("=" * 80)
        
        # Sort by annualized return
        sorted_results = sorted(results, key=lambda r: r.annualized_return.value, reverse=True)
        
        for metrics in sorted_results:
            print(f"\n🏷️  {metrics.ticker.symbol}")
            print(f"   💸 Start Price:        {metrics.start_price}")
            print(f"   💰 End Price:          {metrics.end_price}")
            print(f"   🔺 Total Return:       {metrics.total_return}")
            print(f"   📈 Annualized Return:  {metrics.annualized_return}")
            print(f"   📊 Volatility:         {metrics.volatility}")
            print(f"   📏 Sharpe Ratio:       {metrics.sharpe_ratio:.2f}")
            print(f"   📉 Max Drawdown:       {metrics.max_drawdown}")
            print(f"   💰 Dividend Yield:     {metrics.dividend_yield}")
            print(f"   📊 Momentum (12-1):    {metrics.momentum_12_1}")
        print("=" * 80)
    
    def _display_data_issues(self, missing_tickers: List[str], tickers_without_start_data: List[str]) -> None:
        """Display information about tickers with data issues."""
        if missing_tickers or tickers_without_start_data:
            print("\n⚠️  DATA AVAILABILITY ISSUES")
            print("=" * 60)
            
            if missing_tickers:
                print(f"❌ No data available for: {', '.join(missing_tickers)}")
                print("   These tickers will be excluded from analysis.")
            
            if tickers_without_start_data:
                print(f"⚠️  No data at start date for: {', '.join(tickers_without_start_data)}")
                print("   These tickers may have incomplete analysis periods.")
                print("   Consider adjusting your start date or excluding these tickers.")
            
            print("=" * 60)
    
    def _display_ticker_comparison(self, comparison) -> None:
        """Display ticker comparison results."""
        print(f"\n🔬 TICKER COMPARISON RESULTS")
        print("=" * 80)
        
        if comparison.best_performer:
            print(f"🏆 Best Performer:     {comparison.best_performer.ticker.symbol} "
                  f"({comparison.best_performer.annualized_return})")
        
        if comparison.worst_performer:
            print(f"📉 Worst Performer:    {comparison.worst_performer.ticker.symbol} "
                  f"({comparison.worst_performer.annualized_return})")
        
        if comparison.best_sharpe:
            print(f"📏 Best Sharpe Ratio:  {comparison.best_sharpe.ticker.symbol} "
                  f"({comparison.best_sharpe.sharpe_ratio:.2f})")
        
        if comparison.lowest_risk:
            print(f"🛡️  Lowest Risk:        {comparison.lowest_risk.ticker.symbol} "
                  f"({comparison.lowest_risk.volatility})")
        
        print("=" * 80)
