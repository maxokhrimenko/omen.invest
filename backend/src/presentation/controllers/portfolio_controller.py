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
from ...infrastructure.color_metrics_service import ColorMetricsService
from ...infrastructure.utils.date_utils import get_previous_working_day_string
from ...infrastructure.table_formatter import TableFormatter
from ...infrastructure.repositories.warehouse_market_repository import WarehouseMarketRepository

class PortfolioController:
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
        
        file_path = input("Enter portfolio file path (default: ../input/test.csv): ").strip()
        if not file_path:
            file_path = "../input/test.csv"
        
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
        
        if choice in ["1", "2"]:
            print("\nSelect display format:")
            print("1. Cards format (current)")
            print("2. Table format")
            
            format_choice = input("Enter format choice (1-2, default: 1): ").strip()
            if not format_choice:
                format_choice = "1"
            
            display_format = "cards" if format_choice == "1" else "table"
            
            if choice == "1":
                self._analyze_all_tickers(display_format)
            elif choice == "2":
                self._analyze_specific_ticker(display_format)
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
        """Generate report."""
        if not self._current_portfolio:
            print("❌ No portfolio loaded. Please load a portfolio first.")
            return
        
        print("\n📋 Generating Report")
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
        
        end_date = input("Enter end date (YYYY-MM-DD, default: previous working day): ").strip()
        if not end_date:
            end_date = get_previous_working_day_string()
        
        return DateRange(start_date, end_date)
    
    def _display_portfolio_summary(self) -> None:
        """Display portfolio summary."""
        if not self._current_portfolio:
            return
        
        print(f"\nPortfolio Summary:")
        print(f"Total positions: {len(self._current_portfolio)}")
        print("Tickers:", ", ".join([t.symbol for t in self._current_portfolio.get_tickers()]))
    
    def _display_portfolio_metrics(self, metrics) -> None:
        """Display portfolio analysis results with color coding."""
        print("\n📊 PORTFOLIO ANALYSIS RESULTS")
        print("=" * 60)
        print(f"💸 Start Value:       {metrics.start_value}")
        print(f"💰 End Value Total:   {metrics.end_value}")
        print(f"📈 End Value Analysis: {metrics.end_value_analysis}")
        print(f"⚠️  End Value Missing: {metrics.end_value_missing}")
        
        # Color-coded metrics
        total_return_colored = self._color_service.colorize_percentage(
            metrics.total_return.value, "total_return", "portfolio"
        )
        print(f"🔺 Total Return:      {total_return_colored}")
        
        annualized_return_colored = self._color_service.colorize_percentage(
            metrics.annualized_return.value, "annualized_return", "portfolio"
        )
        print(f"📈 Annualized Return: {annualized_return_colored}")
        
        volatility_colored = self._color_service.colorize_percentage(
            metrics.volatility.value, "volatility", "portfolio"
        )
        print(f"📊 Volatility:        {volatility_colored}")
        
        sharpe_colored = self._color_service.colorize_ratio(
            metrics.sharpe_ratio, "sharpe_ratio", "portfolio"
        )
        print(f"📏 Sharpe Ratio:      {sharpe_colored}")
        
        max_drawdown_colored = self._color_service.colorize_percentage(
            metrics.max_drawdown.value, "max_drawdown", "portfolio"
        )
        print(f"📉 Max Drawdown:      {max_drawdown_colored}")
        
        sortino_colored = self._color_service.colorize_ratio(
            metrics.sortino_ratio, "sortino_ratio", "portfolio"
        )
        print(f"📈 Sortino Ratio:     {sortino_colored}")
        
        calmar_colored = self._color_service.colorize_ratio(
            metrics.calmar_ratio, "calmar_ratio", "portfolio"
        )
        print(f"📊 Calmar Ratio:      {calmar_colored}")
        
        var_colored = self._color_service.colorize_percentage(
            metrics.var_95.value, "var_95", "portfolio"
        )
        print(f"⚠️  VaR (95%):        {var_colored}")
        
        beta_colored = self._color_service.colorize_ratio(
            metrics.beta, "beta", "portfolio"
        )
        print(f"β  Beta:             {beta_colored}")
        print("=" * 60)
    
    def _analyze_all_tickers(self, display_format: str = "cards") -> None:
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
            self._display_ticker_results(results, display_format)
    
    def _analyze_specific_ticker(self, display_format: str = "cards") -> None:
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
                    self._display_ticker_results([response.metrics], display_format)
                else:
                    if not response.has_data_at_start and response.first_available_date:
                        print(f"❌ {selected_ticker.symbol}: No data at start date. First available: {response.first_available_date}")
                    else:
                        print(f"❌ {response.message}")
            else:
                print("❌ Invalid ticker number.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    def _display_ticker_results(self, results, display_format: str = "cards") -> None:
        """Display ticker analysis results."""
        print(f"\n📈 TICKER ANALYSIS RESULTS ({len(results)} tickers)")
        print("=" * 80)
        
        # Sort by annualized return
        sorted_results = sorted(results, key=lambda r: r.annualized_return.value, reverse=True)
        
        if display_format == "table":
            self._display_ticker_results_table(sorted_results)
        else:
            self._display_ticker_results_cards(sorted_results)
        
        print("=" * 80)
    
    def _display_ticker_results_cards(self, results) -> None:
        """Display ticker analysis results in cards format with color coding."""
        for metrics in results:
            # Colorize ticker symbol
            ticker_colored = self._color_service.colorize_ticker_symbol(metrics.ticker.symbol)
            print(f"\n🏷️  {ticker_colored}")
            print(f"   💸 Start Price:        {metrics.start_price}")
            print(f"   💰 End Price:          {metrics.end_price}")
            
            # Color-coded metrics
            total_return_colored = self._color_service.colorize_percentage(
                metrics.total_return.value, "annualized_return", "ticker"
            )
            print(f"   🔺 Total Return:       {total_return_colored}")
            
            annualized_return_colored = self._color_service.colorize_percentage(
                metrics.annualized_return.value, "annualized_return", "ticker"
            )
            print(f"   📈 Annualized Return:  {annualized_return_colored}")
            
            volatility_colored = self._color_service.colorize_percentage(
                metrics.volatility.value, "volatility", "ticker"
            )
            print(f"   📊 Volatility:         {volatility_colored}")
            
            sharpe_colored = self._color_service.colorize_ratio(
                metrics.sharpe_ratio, "sharpe_ratio", "ticker"
            )
            print(f"   📏 Sharpe Ratio:       {sharpe_colored}")
            
            max_drawdown_colored = self._color_service.colorize_percentage(
                metrics.max_drawdown.value, "max_drawdown", "ticker"
            )
            print(f"   📉 Max Drawdown:       {max_drawdown_colored}")
            
            dividend_yield_colored = self._color_service.colorize_percentage(
                metrics.dividend_yield.value, "dividend_yield", "ticker"
            )
            print(f"   💰 Dividend Yield:     {dividend_yield_colored}")
            
            momentum_colored = self._color_service.colorize_percentage(
                metrics.momentum_12_1.value, "momentum_12_1", "ticker"
            )
            print(f"   📊 Momentum (12-1):    {momentum_colored}")
    
    def _display_ticker_results_table(self, results) -> None:
        """Display ticker analysis results in table format with color coding."""
        # Define column headers
        headers = [
            "Ticker", "Start $", "End $", "TotRet", "AnnRet", 
            "Volatility", "Sharpe", "MaxDD", "AnnDiv", "DivYield", "Freq", "Momentum"
        ]
        
        # Prepare data rows with color coding
        data_rows = []
        for metrics in results:
            # Colorize each metric
            ticker_colored = self._color_service.colorize_ticker_symbol(metrics.ticker.symbol)
            total_return_colored = self._color_service.colorize_percentage(
                metrics.total_return.value, "annualized_return", "ticker"
            )
            annualized_return_colored = self._color_service.colorize_percentage(
                metrics.annualized_return.value, "annualized_return", "ticker"
            )
            volatility_colored = self._color_service.colorize_percentage(
                metrics.volatility.value, "volatility", "ticker"
            )
            sharpe_colored = self._color_service.colorize_ratio(
                metrics.sharpe_ratio, "sharpe_ratio", "ticker"
            )
            max_drawdown_colored = self._color_service.colorize_percentage(
                metrics.max_drawdown.value, "max_drawdown", "ticker"
            )
            annualized_dividend_colored = f"${metrics.annualized_dividend.amount:.2f}"
            dividend_yield_colored = self._color_service.colorize_percentage(
                metrics.dividend_yield.value, "dividend_yield", "ticker"
            )
            frequency_colored = self._color_frequency(metrics.dividend_frequency)
            momentum_colored = self._color_service.colorize_percentage(
                metrics.momentum_12_1.value, "momentum_12_1", "ticker"
            )
            
            row_data = [
                ticker_colored,
                f"${metrics.start_price.amount:.2f}",
                f"${metrics.end_price.amount:.2f}",
                total_return_colored,
                annualized_return_colored,
                volatility_colored,
                sharpe_colored,
                max_drawdown_colored,
                annualized_dividend_colored,
                dividend_yield_colored,
                frequency_colored,
                momentum_colored
            ]
            data_rows.append(row_data)
        
        # Use TableFormatter to create properly aligned table
        table = TableFormatter.create_table(headers, data_rows)
        print(f"\n{table}")
    
    def _color_frequency(self, frequency: str) -> str:
        """Color code dividend frequency for display."""
        if frequency == "Monthly":
            return f"🟢 {frequency}"
        elif frequency == "Quarterly":
            return f"🔵 {frequency}"
        elif frequency == "Semi-Annual":
            return f"🟡 {frequency}"
        elif frequency == "Annual":
            return f"🟠 {frequency}"
        elif frequency == "Irregular":
            return f"🔴 {frequency}"
        else:
            return f"⚪ {frequency}"
    
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
    
    def display_warehouse_metrics(self, market_repo: WarehouseMarketRepository) -> None:
        """Display warehouse observability metrics."""
        if not isinstance(market_repo, WarehouseMarketRepository):
            print("\n📊 Warehouse metrics not available (not using warehouse repository)")
            return
        
        metrics = market_repo.get_observability_metrics()
        
        print("\n📊 WAREHOUSE METRICS")
        print("=" * 50)
        print(f"🏪 Warehouse Hits:        {metrics['warehouse_hits']}")
        print(f"❌ Warehouse Misses:      {metrics['warehouse_misses']}")
        print(f"🌐 Yahoo API Calls:       {metrics['yahoo_calls']}")
        print(f"📈 Missing Range Segments: {metrics['missing_range_segments']}")
        print(f"📅 Calendar Skipped Days:  {metrics['calendar_skipped_days']}")
        
        db_size = metrics['database_size_bytes']
        if db_size > 0:
            if db_size < 1024:
                size_str = f"{db_size} B"
            elif db_size < 1024 * 1024:
                size_str = f"{db_size / 1024:.1f} KB"
            else:
                size_str = f"{db_size / (1024 * 1024):.1f} MB"
            print(f"💾 Database Size:         {size_str}")
        else:
            print(f"💾 Database Size:         0 B")
        
        print("=" * 50)
    
    @log_user_action("show_warehouse_metrics")
    def show_warehouse_metrics(self) -> None:
        """Display warehouse observability metrics."""
        print("\n🏪 Warehouse Metrics")
        print("─" * 50)
        
        # Get the market repository from the analyze portfolio use case
        market_repo = self._analyze_portfolio_use_case._market_data_repo
        self.display_warehouse_metrics(market_repo)
