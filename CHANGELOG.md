# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.0] - 2025-09-21

### 🏪 Comprehensive Warehouse System with Dividend Absence Caching

This release introduces a complete warehouse system with read-through caching for market data, including intelligent dividend absence caching that eliminates repeated API calls for periods with no dividends.

### ✨ Added
- **Warehouse System**: Complete read-through caching layer using embedded SQLite database
- **Dividend Absence Caching**: Stores information about periods with no dividends to prevent repeated API calls
- **Trading-Day Awareness**: Smart gap filling that only fetches missing trading days, skipping weekends and holidays
- **Feature Flag Support**: `WAREHOUSE_ENABLED` environment variable for instant rollback capability
- **Comprehensive Observability**: Detailed metrics for warehouse hits, misses, Yahoo calls, and performance timing
- **Database Management**: Administrative tools for warehouse statistics, backup, and cleanup
- **Performance Monitoring**: Real-time metrics display through CLI interface

### 🔄 Changed
- **Market Data Repository**: Now uses `WarehouseMarketRepository` with transparent caching
- **Dividend Data Handling**: Always stores coverage information, whether dividends exist or not
- **Performance**: Massive speedup for repeated requests (100x+ faster on subsequent calls)
- **API Efficiency**: Eliminates unnecessary Yahoo Finance API calls through intelligent caching
- **Default Input File**: Changed from `input/input.csv` to `input/test.csv`

### 🏗️ Technical Architecture

#### Warehouse Components:
- **`WarehouseService`**: Core SQLite database operations with WAL mode
- **`TradingDayService`**: Trading day calculation with US holiday awareness
- **`WarehouseMarketRepository`**: Read-through cache decorator for market data
- **`WarehouseConfig`**: Feature flag and configuration management

#### Database Schema:
- **`market_data`**: Price history storage with ticker, date, close_price
- **`dividend_data`**: Dividend payments storage with ticker, date, dividend_amount
- **`dividend_coverage`**: Coverage tracking for periods checked (with/without dividends)

#### Performance Features:
- **Read-Through Caching**: Transparent layer that checks warehouse before Yahoo API
- **Gap Filling**: Fetches only missing trading-day ranges from Yahoo
- **Batching**: Groups multiple missing ranges into single API calls
- **Coverage Thresholds**: 80% coverage threshold to account for market holidays

### 🚀 Performance Improvements
- **First Call**: Normal speed (fetches from Yahoo, stores in warehouse)
- **Subsequent Calls**: 100x+ faster (served from warehouse cache)
- **Dividend Data**: 542x faster on repeated calls
- **Zero Repeated API Calls**: Once a period is checked, no more Yahoo calls
- **Memory Efficient**: Embedded SQLite with WAL mode for optimal performance

### 📊 Observability Metrics
- **warehouse_hits**: Number of requests served from cache
- **warehouse_misses**: Number of requests that required Yahoo API calls
- **yahoo_calls**: Total number of Yahoo API calls made
- **missing_range_segments**: Number of missing date ranges identified
- **calendar_skipped_days**: Number of non-trading days skipped
- **Database Size**: Real-time warehouse database size monitoring

### 🛠️ Administrative Tools
- **Warehouse Statistics**: Comprehensive database statistics and coverage information
- **Backup/Restore**: Database backup and restore functionality
- **Data Cleanup**: Clear specific tickers or entire warehouse
- **Log Management**: Enhanced logging for warehouse operations

### 🔧 Technical Details
- **SQLite Database**: `./warehouse/warehouse.sqlite` with WAL mode enabled
- **ACID Compliance**: Transactional updates with proper error handling
- **Cross-Platform**: Single-file database with no external dependencies
- **Idempotent Operations**: Safe to re-run without creating duplicates
- **Trading-Day Logic**: Uses same effective trading-day reality as current product

### 🎯 Key Benefits
- **Massive Performance Gains**: 100x+ speedup for repeated requests
- **API Efficiency**: Eliminates unnecessary external API calls
- **Complete Coverage**: Tracks both dividend presence and absence
- **Transparent Operation**: No changes to existing data contracts or interfaces
- **Production Ready**: Feature flag for safe rollout and instant rollback

## [4.0.3] - 2025-09-21

### 🎨 Color-Coded Metrics & Enhanced Display

This release introduces comprehensive color-coding for all financial metrics based on performance thresholds, along with improved table formatting and display options.

### ✨ Added
- **Color-Coded Metrics System**: Complete color-coding implementation based on METRICS_MEMORANDUM.md thresholds
- **MetricsColorService**: Dedicated service for color-coding financial metrics with context-aware thresholds
- **Table Display Format**: New table view option for ticker analysis alongside existing cards format
- **TableFormatter Utility**: Advanced table formatting that properly handles ANSI color codes
- **Display Format Selection**: Users can choose between cards and table formats for ticker analysis
- **Context-Aware Color Coding**: Different thresholds for portfolio vs ticker metrics
- **Special Metric Handling**: Proper color logic for metrics where lower values are better (max_drawdown, volatility, etc.)

### 🔄 Changed
- **Ticker Analysis Display**: Enhanced with color-coded metrics and format selection
- **Portfolio Analysis Display**: All consolidated metrics now color-coded
- **Table Formatting**: Fixed alignment issues caused by ANSI color codes
- **User Interface**: Added display format selection in ticker analysis menu
- **Controller Architecture**: Integrated color service with dependency injection

### 🎯 Color Coding Implementation

#### Portfolio Metrics (Consolidated):
- **Total Return**: Red <10%, Yellow 10-30%, Green >30%
- **Annualized Return**: Red <5%, Yellow 5-15%, Green >15%
- **Sharpe Ratio**: Red <0.5, Yellow 0.5-1.5, Green >1.5
- **Sortino Ratio**: Red <1.0, Yellow 1.0-2.0, Green >2.0
- **Calmar Ratio**: Red <0.5, Yellow 0.5-1.0, Green >1.0
- **Max Drawdown**: Red >-30%, Yellow -30% to -15%, Green >-15%
- **Volatility**: Red >20%, Yellow 10-20%, Green <10%
- **VaR (95%)**: Red >-2%, Yellow -2% to -1%, Green >-1%
- **Beta**: Red >1.3, Yellow 0.7-1.3, Green <0.7

#### Ticker Metrics (Individual):
- **Annualized Return**: Red <5%, Yellow 5-20%, Green >20%
- **Sharpe Ratio**: Red <0.5, Yellow 0.5-1.5, Green >1.5
- **Sortino Ratio**: Red <0.8, Yellow 0.8-2.0, Green >2.0
- **Max Drawdown**: Red >-50%, Yellow -50% to -30%, Green >-30%
- **Volatility**: Red >50%, Yellow 30-50%, Green <30%
- **Beta**: Red >1.5, Yellow 0.5-1.5, Green <0.5
- **VaR (95%)**: Red >-4%, Yellow -4% to -2%, Green >-2%
- **Momentum (12-1)**: Red <0%, Yellow 0-20%, Green >20%
- **Dividend Yield**: Red <1%, Yellow 1-4%, Green >4%
- **Maximum Yield**: Red <2%, Yellow 2-6%, Green >6%

### 🛠️ Technical Architecture

#### New Components:
- **`MetricsColorService`**: Interface and implementation for color-coding metrics
- **`TableFormatter`**: Utility for proper table formatting with color codes
- **Color Code System**: ANSI escape sequences with proper terminal compatibility
- **Dynamic Column Sizing**: Automatic column width calculation based on content

#### SOLID Principles:
- **Single Responsibility**: Dedicated color service with single responsibility
- **Open/Closed**: Extensible color system for new metrics
- **Dependency Inversion**: Controller depends on color service abstraction

### 🐛 Fixed
- **Table Alignment**: Fixed column misalignment caused by ANSI color codes
- **Display Width Calculation**: Proper handling of color codes in width calculations
- **Max Drawdown Logic**: Corrected color logic for negative values
- **Column Sizing**: Dynamic column sizing based on actual content width

### 📊 User Experience Improvements
- **Visual Clarity**: Instant visual feedback on metric performance
- **Format Flexibility**: Choice between detailed cards and compact table views
- **Consistent Formatting**: Properly aligned tables with color coding
- **Professional Appearance**: Clean, readable output with color-coded insights

### 🔧 Technical Details
- **ANSI Color Support**: Full terminal color compatibility
- **Regex Pattern Matching**: Efficient ANSI code detection and removal
- **Dynamic Width Calculation**: Real-time column sizing based on content
- **Context-Aware Thresholds**: Different color rules for portfolio vs ticker metrics
- **Extensible Design**: Easy addition of new metrics and color rules

## [4.0.2] - 2025-09-21

### 🔍 Data Validation & Missing Data Detection

This release introduces comprehensive data validation to ensure analysis accuracy and provide clear feedback about data availability issues.

### ✨ Added
- **Missing Data Detection**: Identifies tickers with no data available at all
- **Start Date Validation**: Detects tickers without data at analysis start date with 5-day business tolerance
- **Data Availability Reporting**: Clear warnings about data availability issues in both portfolio and ticker analysis
- **Business Day Tolerance**: 5-day tolerance accounts for weekends, holidays, and data availability delays
- **User-Friendly Warnings**: Comprehensive data issues display with actionable recommendations
- **Enhanced Response Structures**: 
  - `AnalyzePortfolioResponse` now includes `missing_tickers` and `tickers_without_start_data` fields
  - `AnalyzeTickerResponse` now includes `has_data_at_start` and `first_available_date` fields

### 🔄 Changed
- **Portfolio Analysis**: Now validates data availability and reports missing tickers
- **Ticker Analysis**: Enhanced with start date validation and data availability reporting
- **Controller Display**: Added `_display_data_issues()` method for comprehensive data warnings
- **User Experience**: Analysis results now include data availability warnings when applicable

### 🐛 Fixed
- **Analysis Accuracy**: Prevents misleading results from incomplete data
- **Data Transparency**: Users now have full visibility into data limitations
- **Business Day Logic**: Proper handling of weekends and holidays in data validation

### 📊 User Experience Improvements
- **Clear Data Warnings**: Users see exactly which tickers have data issues
- **Actionable Recommendations**: Suggestions to adjust analysis parameters or exclude problematic tickers
- **Transparent Reporting**: Full visibility into how missing data affects analysis accuracy

### 🔧 Technical Details
- **Data Validation Logic**: `_identify_data_issues()` method in `AnalyzePortfolioUseCase`
- **Business Day Tolerance**: 5-day tolerance for realistic data availability validation
- **Enhanced Logging**: Detailed logging of data validation issues
- **Controller Integration**: Seamless integration of data warnings in user interface

## [4.0.0] - 2025-09-19

### 🚀 Major Architecture Refactoring

This is a **complete rewrite** of the application following Clean Architecture principles and SOLID design patterns.

### ✨ Added
- **Clean Architecture Implementation**: Complete separation of concerns across domain, application, infrastructure, and presentation layers
- **Interactive CLI Interface**: User-friendly menu system for all operations
- **Domain-Driven Design**: Business entities (Ticker, Position, Portfolio) and value objects (Money, Percentage, DateRange)
- **Use Case Pattern**: Dedicated use cases for LoadPortfolio, AnalyzePortfolio, AnalyzeTicker, and CompareTickers
- **Repository Pattern**: Abstract interfaces with concrete implementations for CSV and YFinance data sources
- **Dependency Injection**: Proper DI container setup in main application
- **Comprehensive Testing**: 38 tests covering unit and integration scenarios
- **Configuration Management**: YAML-based settings with Settings service
- **Enhanced Error Handling**: Robust error handling across all layers
- **Type Safety**: Full type hints throughout the codebase

### 🔄 Changed
- **Application Entry Point**: New `main.py` with interactive CLI (replaces direct script execution)
- **Data Flow**: Request/Response pattern for all operations
- **Error Handling**: Centralized error handling with user-friendly messages
- **Testing Strategy**: Test-driven approach with comprehensive coverage
- **Documentation**: Complete rewrite with architecture documentation

### 🏗️ Technical Architecture
```
src/
├── domain/                 # Business logic and rules
│   ├── entities/          # Core business objects
│   └── value_objects/     # Immutable value types
├── application/           # Use cases and business workflows
│   ├── use_cases/        # Business use cases
│   └── interfaces/       # Repository interfaces
├── infrastructure/       # External concerns
│   ├── repositories/     # Data access implementations
│   └── config/          # Configuration management
└── presentation/         # User interface
    ├── cli/             # Command-line interface
    └── controllers/     # Application controllers
```

### 📊 Performance Improvements
- **Faster Execution**: Optimized data processing and analysis
- **Memory Efficiency**: Better resource management
- **Scalability**: Architecture supports easy extension for new features

### 🧪 Testing
- **Unit Tests**: 34 tests for core business logic
- **Integration Tests**: 4 tests for end-to-end workflows
- **Test Coverage**: 100% coverage for domain layer
- **CI Ready**: Full test automation support

### 📚 Documentation
- **README.md**: Complete rewrite with new usage instructions
- **ARCHITECTURE.md**: Detailed technical architecture documentation
- **Implementation Plan**: Comprehensive development tracking

### 🔄 Backwards Compatibility
- **Legacy Scripts Preserved**: Original scripts remain functional
- **Same CSV Format**: No changes to input data format
- **Same Metrics**: All original calculations preserved and enhanced

### 🚀 Migration Guide
To use the new application:
1. Run `python main.py` instead of individual scripts
2. Follow the interactive menu for all operations
3. Legacy scripts still available: `python portfolio_analysis_consolidated.py`

---

## [3.1.0] - 2024-03-19

### Changed
- Moved portfolio data from hardcoded string to CSV file
- Added input directory for data files
- Enhanced error handling for file operations
- Updated portfolio parsing to handle CSV format
- Standardized position values to 2 decimal places

### Files Changed
- Modified `portfolio_analysis_consolidated.py`
- Modified `portfolio_analysis_by_one.py`
- Created `input/input.csv`
- Updated `.gitignore` to handle input directory

### Technical Details
- Added CSV file parsing with pandas
- Implemented file existence checks
- Added column validation for CSV format
- Enhanced error messages for file operations
- Standardized position number formatting

## [3.0.0] - 2024-03-19

### Added
- Initial project structure
- Core portfolio analysis functionality
- Per-ticker analysis with dividend tracking
- Color-coded yield indicators
- Comprehensive documentation

### Changed
- N/A (Initial release)

### Files Changed
- Created `portfolio_analysis_consolidated.py`
- Created `portfolio_analysis_by_one.py`
- Created `README.md`
- Created `CHANGELOG.md`
- Created `.gitignore`
- Created `input/` directory

### Technical Details
- Implemented portfolio data parsing
- Added price data loading and validation
- Created utility functions for metrics calculation
- Added dividend analysis functionality
- Implemented color-coded output formatting 