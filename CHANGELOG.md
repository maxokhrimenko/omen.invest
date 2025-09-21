# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0] - 2025-09-21

### 🚀 Full-Stack Implementation with FastAPI & React

This release introduces a complete full-stack implementation with a FastAPI backend and React frontend, transforming the application from a CLI-only tool to a modern web application.

### ✨ Added

#### Backend API (FastAPI)
- **REST API Endpoints**: Complete REST API with FastAPI framework
- **Portfolio Management**: Upload, retrieve, and clear portfolio endpoints
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **File Upload**: Multipart file upload support for CSV portfolio files
- **Health Check**: System health monitoring endpoint
- **Error Handling**: Comprehensive HTTP error handling with proper status codes
- **Dependency Injection**: Clean dependency injection for API endpoints
- **Pydantic Models**: Type-safe request/response models

#### Frontend Application (React + TypeScript)
- **Modern React Setup**: React 19 with TypeScript and Vite build system
- **Portfolio Upload Interface**: Drag-and-drop CSV file upload with validation
- **Portfolio Management**: View, clear, and manage portfolio data
- **API Integration**: Axios-based API service with interceptors
- **Responsive Design**: Tailwind CSS for modern, responsive UI
- **Component Architecture**: Modular React components with proper separation
- **Type Safety**: Full TypeScript integration with API types
- **Error Handling**: User-friendly error messages and loading states

#### Development Infrastructure
- **Local Development Runner**: Comprehensive script for full-stack development
- **Concurrent Development**: Backend and frontend run simultaneously
- **Port Management**: Automatic port conflict resolution
- **Dependency Management**: Automated setup for both Python and Node.js
- **Process Management**: Graceful start/stop of all services
- **Status Monitoring**: Real-time service status checking

### 🔄 Changed

#### API Architecture
- **FastAPI Integration**: Backend now exposes REST API endpoints
- **Request/Response Pattern**: Standardized API request/response format
- **CORS Configuration**: Proper CORS setup for frontend-backend communication
- **File Handling**: Temporary file management for CSV uploads
- **Error Responses**: Structured error responses with proper HTTP status codes

#### Frontend Architecture
- **Component-Based Design**: Modular React components for maintainability
- **API Service Layer**: Centralized API communication with error handling
- **State Management**: React hooks for local state management
- **Type Definitions**: Comprehensive TypeScript interfaces for API contracts
- **Build System**: Vite for fast development and optimized builds

#### Development Workflow
- **Full-Stack Development**: Single command to start entire application stack
- **Hot Reloading**: Both backend and frontend support hot reloading
- **Environment Configuration**: Environment variable support for API URLs
- **Cross-Platform**: Works on macOS, Linux, and Windows

### 🏗️ Technical Implementation

#### Backend API Endpoints
```
GET  /health                    # Health check
POST /portfolio/upload          # Upload portfolio CSV
GET  /portfolio                 # Get current portfolio
DELETE /portfolio               # Clear portfolio
GET  /portfolio/analysis        # Analyze portfolio (placeholder)
GET  /portfolio/tickers/analysis # Analyze tickers (placeholder)
```

#### Frontend Components
- **PortfolioUpload**: File upload with drag-and-drop support
- **PortfolioTable**: Tabular display of portfolio data
- **MainLayout**: Application layout with navigation
- **Header/Sidebar**: Navigation components
- **DashboardPage**: Main dashboard interface
- **PortfolioUploadPage**: Dedicated upload page

#### API Service Integration
- **Axios Configuration**: Centralized HTTP client with interceptors
- **Error Handling**: Automatic error transformation and user feedback
- **Request/Response Logging**: Development-time API call logging
- **Type Safety**: Full TypeScript integration with API responses

### 🚀 Development Experience

#### Local Development
```bash
# Start full-stack application
./local/run.sh start

# Start only backend
./local/run.sh backend

# Start only frontend  
./local/run.sh frontend

# Setup project
./local/run.sh setup

# Check status
./local/run.sh status
```

#### Service URLs
- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs (FastAPI auto-docs)

### 📊 User Interface Features

#### Portfolio Upload
- **Drag & Drop**: Intuitive file upload interface
- **File Validation**: CSV format validation with user feedback
- **Progress Indicators**: Upload progress and success/error states
- **Error Messages**: Clear, actionable error messages

#### Portfolio Management
- **Data Display**: Clean tabular display of portfolio positions
- **Action Buttons**: Clear portfolio and refresh functionality
- **Status Indicators**: Visual feedback for all operations
- **Responsive Design**: Works on desktop and mobile devices

### 🔧 Technical Stack

#### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and serialization
- **Python Multipart**: File upload handling
- **Existing Clean Architecture**: All existing business logic preserved

#### Frontend
- **React 19**: Latest React with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **Lucide React**: Modern icon library
- **React Router**: Client-side routing

### 🎯 Benefits

#### Developer Experience
- **Full-Stack Development**: Single repository with both frontend and backend
- **Hot Reloading**: Instant feedback during development
- **Type Safety**: End-to-end type safety from API to UI
- **Modern Tooling**: Latest development tools and frameworks
- **Easy Setup**: One-command project setup and start

#### User Experience
- **Web Interface**: Modern, responsive web application
- **Intuitive Upload**: Drag-and-drop file upload experience
- **Real-time Feedback**: Immediate visual feedback for all operations
- **Error Handling**: Clear, actionable error messages
- **Mobile Friendly**: Responsive design works on all devices

#### Architecture Benefits
- **Separation of Concerns**: Clear separation between frontend and backend
- **API-First Design**: RESTful API enables multiple client types
- **Scalability**: Independent scaling of frontend and backend
- **Maintainability**: Modular architecture with clear boundaries
- **Future-Ready**: Easy to extend with new features and clients

### 🔮 Future Enhancements

#### Planned Features
- **Portfolio Analysis UI**: Complete portfolio analysis interface
- **Ticker Analysis UI**: Individual ticker analysis with charts
- **Real-time Data**: Live market data updates
- **Advanced Charts**: Interactive financial charts and visualizations
- **User Authentication**: User accounts and portfolio persistence
- **Export Features**: PDF and Excel export capabilities

#### Technical Roadmap
- **Database Integration**: PostgreSQL for production data storage
- **Authentication**: JWT-based user authentication
- **Caching**: Redis for improved performance
- **Monitoring**: Application performance monitoring
- **Testing**: Comprehensive test suite for both frontend and backend
- **Deployment**: Docker containerization and cloud deployment

## [4.1.2] - 2025-09-21

### 🏗️ Full-Stack Repository Restructure

This release restructures the entire repository to support full-stack development with clear separation between backend, frontend, and database components.

### ✨ Added
- **Frontend Directory Structure**: Complete frontend folder structure with modern web development setup
- **Database Directory**: Organized database files in dedicated directory
- **Shared Resources**: Common types, schemas, and utilities for both frontend and backend
- **Enhanced Documentation**: Comprehensive documentation for full-stack architecture
- **Build Scripts**: Development and deployment script directories
- **Configuration Management**: Centralized configuration files

### 🔄 Changed
- **Repository Structure**: Reorganized from backend-only to full-stack architecture
- **Input Data Location**: Moved input files to root directory for better accessibility
- **Documentation Updates**: Updated all documentation to reflect new structure
- **Path References**: Updated all file paths to work with new directory structure

### 📁 New Directory Structure
```
omen.invest/
├── backend/                    # Backend API and Services
├── frontend/                   # Frontend Application (Ready for development)
├── database/                   # Database and Data Storage
├── shared/                     # Shared Resources
├── docs/                       # Documentation
├── scripts/                    # Build and deployment scripts
├── input/                      # Input data files
└── config/                     # Configuration files
```

### 🎯 Benefits
- **Scalable Development**: Independent development of frontend and backend
- **Clear Separation**: Well-defined boundaries between components
- **Future-Ready**: Prepared for modern web development
- **Maintainable**: Logical organization for easier maintenance
- **Deployable**: Each component can be deployed independently

### 🔧 Technical Details
- **Backend**: Python with Clean Architecture (unchanged functionality)
- **Frontend**: Modern web framework ready (React/Vue/Angular)
- **Database**: SQLite warehouse with caching
- **Shared**: Common types and utilities
- **Documentation**: Comprehensive technical documentation

## [4.1.1] - 2025-09-21

### 🎯 Annualized Dividend Calculation System

This release introduces a comprehensive dividend analysis system that properly handles different payment frequencies and provides accurate annualized dividend metrics for fair comparison across all stocks.

### ✨ Added
- **Automatic Frequency Detection**: Intelligently detects dividend payment patterns (Monthly, Quarterly, Semi-Annual, Annual, Irregular)
- **Smart Annualization**: Calculates proper annualized dividends based on detected payment frequency
- **Enhanced Display**: New table columns showing annualized dividend amount, yield, and payment frequency
- **Frequency Color Coding**: Visual indicators for different payment frequencies (🟢 Monthly, 🔵 Quarterly, 🟡 Semi-Annual, 🟠 Annual, 🔴 Irregular)
- **Accurate Yield Calculation**: Uses average price over analysis period for consistent yield calculations

### 🔄 Changed
- **Dividend Yield Calculation**: Completely redesigned to use proper annualization instead of cumulative period totals
- **Table Format**: Updated to show "AnnDiv" (Annualized Dividend) and "Freq" (Frequency) columns
- **TickerMetrics Class**: Added `dividend_frequency` and `annualized_dividend` fields
- **Calculation Logic**: Now handles different payment frequencies correctly for fair comparison

### 🏗️ Technical Implementation
- **Frequency Detection Algorithm**: Analyzes payment intervals to determine frequency patterns
- **Annualization Formulas**: 
  - Monthly: `total_dividends × (12 / payment_count)`
  - Quarterly: `total_dividends × (4 / payment_count)`
  - Semi-Annual: `total_dividends × (2 / payment_count)`
  - Annual: `total_dividends / period_years`
  - Irregular: `total_dividends / period_years`
- **Type Safety**: Proper handling of Decimal and float conversions for calculations

### 📊 Example Results
| Stock | Frequency | Period Dividends | Annualized Dividend | Annualized Yield |
|-------|-----------|------------------|-------------------|------------------|
| PM | Quarterly | $8.00 | $5.33 | 4.07% |
| JEPI | Monthly | $7.13 | $4.50 | 8.37% |
| GLPI | Quarterly | $5.36 | $3.06 | 6.77% |

### 🎯 Benefits
- **Comparable Metrics**: All dividend yields are now properly annualized for fair comparison
- **Frequency Awareness**: Shows payment frequency to understand dividend patterns
- **Accurate Calculations**: Handles different payment schedules correctly
- **Industry Standard**: Follows proper financial calculation methodology
- **Visual Clarity**: Color-coded frequency indicators for quick understanding

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