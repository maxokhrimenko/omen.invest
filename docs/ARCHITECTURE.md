# 🏗️ Architecture Documentation

## Overview

The Portfolio Analysis Tool has been completely refactored to follow **Clean Architecture** principles, ensuring separation of concerns, testability, and maintainability. The application now features a full-stack implementation with a FastAPI backend and React frontend, providing both CLI and web interfaces for portfolio analysis. This document provides a comprehensive overview of the application's architecture, design patterns, and data flow.

## 🎯 Architectural Principles

### Clean Architecture
The application follows Uncle Bob's Clean Architecture, organizing code into layers with clear dependencies:

1. **Domain Layer** (innermost): Business logic and rules
2. **Application Layer**: Use cases and business workflows
3. **Infrastructure Layer**: External systems and frameworks
4. **Presentation Layer** (outermost): User interface and delivery mechanisms

### SOLID Principles
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Many client-specific interfaces are better than one general-purpose interface
- **Dependency Inversion**: Depend on abstractions, not concretions

## 📦 Directory Structure

```
portfolio-analysis-tool/
├── src/                           # Source code
│   ├── domain/                    # 🏛️ Domain Layer
│   │   ├── entities/              # Business entities
│   │   │   ├── __init__.py
│   │   │   ├── ticker.py          # Ticker symbol entity
│   │   │   ├── position.py        # Portfolio position entity
│   │   │   └── portfolio.py       # Portfolio aggregate root
│   │   ├── value_objects/         # Immutable value types
│   │   │   ├── __init__.py
│   │   │   ├── money.py           # Money with currency
│   │   │   ├── percentage.py      # Percentage values
│   │   │   └── date_range.py      # Date range handling
│   │   ├── exceptions/            # Domain-specific exceptions
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── application/               # 🔄 Application Layer
│   │   ├── use_cases/             # Business use cases
│   │   │   ├── __init__.py
│   │   │   ├── load_portfolio.py  # Load portfolio from source
│   │   │   ├── analyze_portfolio.py # Portfolio analysis
│   │   │   ├── analyze_ticker.py  # Individual ticker analysis
│   │   │   └── compare_tickers.py # Ticker comparison
│   │   ├── services/              # Application services
│   │   │   └── __init__.py
│   │   ├── interfaces/            # Repository interfaces
│   │   │   ├── __init__.py
│   │   │   └── repositories.py    # Abstract repository interfaces
│   │   └── __init__.py
│   ├── infrastructure/            # 🔧 Infrastructure Layer
│   │   ├── repositories/          # Data access implementations
│   │   │   ├── __init__.py
│   │   │   ├── csv_portfolio_repository.py  # CSV file operations
│   │   │   ├── yfinance_market_repository.py # Market data from yfinance
│   │   │   └── warehouse_market_repository.py # Warehouse-enabled caching layer
│   │   ├── warehouse/             # Warehouse system components
│   │   │   ├── __init__.py
│   │   │   ├── warehouse_service.py # Core SQLite database operations
│   │   │   ├── trading_day_service.py # Trading day calculations
│   │   │   └── config/            # Warehouse configuration
│   │   │       └── warehouse_config.py
│   │   ├── logging/               # Comprehensive logging system
│   │   │   ├── __init__.py
│   │   │   ├── logger_service.py  # Centralized logging service
│   │   │   └── decorators.py      # Logging decorators
│   │   ├── color_metrics_service.py # Color-coding service for metrics
│   │   ├── table_formatter.py     # Table formatting utility
│   │   └── services/              # External service integrations
│   │       └── __init__.py
│   │   ├── config/                # Configuration management
│   │   │   ├── __init__.py
│   │   │   └── settings.py        # Settings service
│   │   └── __init__.py
│   └── presentation/              # 🎨 Presentation Layer
│       ├── cli/                   # Command-line interface
│       │   ├── __init__.py
│       │   └── menu.py            # Interactive menu system
│       ├── controllers/           # Application controllers
│       │   ├── __init__.py
│       │   └── portfolio_controller.py # Portfolio operations controller
│       └── __init__.py
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   │   ├── __init__.py
│   │   ├── test_value_objects.py  # Value object tests
│   │   └── test_entities.py       # Entity tests
│   ├── integration/               # Integration tests
│   │   ├── __init__.py
│   │   └── test_portfolio_analysis.py # End-to-end tests
│   └── e2e/                       # End-to-end tests
│       └── __init__.py
├── admin/                         # Administrative tools
│   ├── __init__.py
│   └── logs_clear.py              # Log management script
├── logs/                          # Log storage
│   ├── sessions/                  # Session-specific logs
│   └── total/                     # All logs across sessions
├── config/                        # Configuration files
│   └── settings.yaml              # Application settings
├── input/                         # Input data
│   └── input.csv                  # Portfolio data
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
├── ARCHITECTURE.md                # This file
├── CHANGELOG.md                   # Version history
└── implementation_plan.md         # Development tracking
```

## 🏛️ Domain Layer

The domain layer contains the core business logic and is independent of any external frameworks or libraries.

### Entities

#### Ticker
- **Purpose**: Represents a stock ticker symbol
- **Responsibilities**: 
  - Validate ticker symbol format
  - Normalize ticker symbols (uppercase, trim whitespace)
  - Provide equality and hashing for collections
- **Business Rules**:
  - Cannot be empty
  - Maximum length of 10 characters
  - Case-insensitive (normalized to uppercase)

#### Position
- **Purpose**: Represents a position in a portfolio
- **Responsibilities**:
  - Link ticker to quantity
  - Calculate position value given price
  - Validate positive quantities
- **Business Rules**:
  - Quantity must be positive
  - Immutable once created

#### Portfolio
- **Purpose**: Aggregate root for a collection of positions
- **Responsibilities**:
  - Manage collection of positions
  - Calculate total portfolio value
  - Provide portfolio-level operations
- **Business Rules**:
  - Cannot be empty
  - Unique positions per ticker (last wins if duplicates)

### Value Objects

#### Money
- **Purpose**: Represents monetary values with currency
- **Responsibilities**:
  - Handle decimal precision for financial calculations
  - Support arithmetic operations (addition, multiplication)
  - Validate non-negative amounts
- **Invariants**:
  - Amount cannot be negative
  - Currency-aware operations

#### Percentage
- **Purpose**: Represents percentage values
- **Responsibilities**:
  - Convert between decimal and percentage representations
  - Format for display
- **Features**:
  - Immutable
  - Type-safe percentage operations

#### DateRange
- **Purpose**: Represents a period between two dates
- **Responsibilities**:
  - Validate date ranges (start <= end)
  - Parse string dates
  - Default to today if end date not provided
- **Business Rules**:
  - Start date cannot be after end date

## 🔄 Application Layer

The application layer orchestrates domain objects to fulfill business use cases.

### Use Cases

#### LoadPortfolioUseCase
- **Input**: `LoadPortfolioRequest` (file path)
- **Output**: `LoadPortfolioResponse` (portfolio, success, message)
- **Responsibilities**:
  - Coordinate with portfolio repository
  - Handle loading errors gracefully
  - Return structured response

#### AnalyzePortfolioUseCase
- **Input**: `AnalyzePortfolioRequest` (portfolio, date range, risk-free rate)
- **Output**: `AnalyzePortfolioResponse` (metrics, success, message, missing_tickers, tickers_without_start_data)
- **Responsibilities**:
  - Fetch market data for all portfolio tickers
  - Calculate portfolio-level metrics
  - Validate data availability with business day tolerance
  - Identify missing tickers and incomplete data scenarios
- **Data Validation Features**:
  - Missing tickers detection (no data available)
  - Start date validation (5-day business tolerance)
  - Comprehensive data availability reporting
- **Calculated Metrics**:
  - Total return, annualized return
  - Volatility, Sharpe ratio, Sortino ratio
  - Maximum drawdown, Calmar ratio
  - Value at Risk (VaR), Beta

#### AnalyzeTickerUseCase
- **Input**: `AnalyzeTickerRequest` (ticker, date range, risk-free rate)
- **Output**: `AnalyzeTickerResponse` (metrics, success, message, has_data_at_start, first_available_date)
- **Responsibilities**:
  - Fetch price and dividend data for single ticker
  - Calculate individual ticker metrics
  - Validate data availability at start date with business day tolerance
  - Handle ticker-specific errors and data validation
- **Data Validation Features**:
  - Start date data availability check (5-day business tolerance)
  - First available date reporting
  - Clear error messages for missing data scenarios

#### CompareTickersUseCase
- **Input**: `CompareTickersRequest` (tickers list, date range, risk-free rate)
- **Output**: `CompareTickersResponse` (comparison, success, message)
- **Responsibilities**:
  - Analyze multiple tickers using AnalyzeTickerUseCase
  - Rank and compare performance
  - Identify best/worst performers

### Request/Response Pattern

All use cases follow a consistent request/response pattern:
```python
@dataclass
class SomeRequest:
    # Input parameters

@dataclass
class SomeResponse:
    result: Optional[SomeResult]
    success: bool
    message: str

class SomeUseCase:
    def execute(self, request: SomeRequest) -> SomeResponse:
        # Business logic
```

## 🔧 Infrastructure Layer

The infrastructure layer handles external concerns like data persistence and API calls.

### Repository Pattern

#### PortfolioRepository (Interface)
```python
class PortfolioRepository(ABC):
    @abstractmethod
    def load(self, file_path: str) -> Portfolio: pass
    
    @abstractmethod
    def save(self, portfolio: Portfolio, file_path: str) -> None: pass
```

#### CsvPortfolioRepository (Implementation)
- **Purpose**: Load/save portfolios from/to CSV files
- **Features**:
  - Robust CSV validation
  - Error handling for file operations
  - Ticker symbol format conversion (BRK.B ↔ BRK-B)

#### MarketDataRepository (Interface)
```python
class MarketDataRepository(ABC):
    @abstractmethod
    def get_price_history(self, tickers: List[Ticker], date_range: DateRange) -> Dict[Ticker, pd.Series]: pass
    
    @abstractmethod
    def get_current_prices(self, tickers: List[Ticker]) -> Dict[Ticker, Money]: pass
    
    @abstractmethod
    def get_dividend_history(self, ticker: Ticker, date_range: DateRange) -> pd.Series: pass
```

#### YFinanceMarketRepository (Implementation)
- **Purpose**: Fetch market data from Yahoo Finance
- **Features**:
  - Handles single and multiple ticker downloads
  - Robust error handling for API failures
  - Data format normalization
  - Dividend history processing

### Logging Infrastructure

#### LoggerService
- **Purpose**: Centralized logging management with session-based separation
- **Features**:
  - Session-based log separation (sessions vs total logs)
  - Human-readable log format with detailed timing
  - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - File-based storage (no console output)
  - Performance monitoring and operation tracking
  - User action logging, API call logging, file operation logging
  - Business operation logging with structured data

#### Logging Decorators
- **Purpose**: Easy application of logging to functions across all layers
- **Available Decorators**:
  - `@log_operation`: General operation logging with timing
  - `@log_user_action`: User interaction logging
  - `@log_api_call`: External API call logging
  - `@log_file_operation`: File I/O operation logging
  - `@log_calculation`: Business calculation logging

#### Log Management
- **Purpose**: Administrative tools for log maintenance
- **Features**:
  - Log statistics and storage usage
  - Session log cleanup
  - Total log cleanup
  - Backup and restore functionality
  - Force operations for automation

### Configuration Management

#### Settings Service
- **Purpose**: Centralized configuration management
- **Features**:
  - YAML-based configuration
  - Default fallbacks
  - Type-safe access methods
  - Environment-specific settings

### Warehouse System (v4.1.0)

#### Overview
The warehouse system provides a transparent read-through caching layer for market data, dramatically improving performance for repeated requests while maintaining complete data accuracy and contract compatibility.

#### WarehouseService
- **Purpose**: Core SQLite database operations with WAL mode
- **Features**:
  - ACID-compliant transactions
  - Idempotent data storage
  - Coverage tracking for both price and dividend data
  - Trading-day aware gap detection
  - Database statistics and management

#### TradingDayService
- **Purpose**: Trading day calculation with US holiday awareness
- **Features**:
  - Weekend and holiday detection
  - Business day tolerance (5-day tolerance for data validation)
  - Integration with existing product's trading day reality
  - Efficient date range processing

#### WarehouseMarketRepository
- **Purpose**: Read-through cache decorator for market data
- **Features**:
  - Transparent caching layer
  - Gap filling for missing data ranges
  - Batching of multiple missing ranges
  - Coverage threshold logic (80% threshold for holidays)
  - Comprehensive observability metrics

#### Database Schema
- **market_data**: Price history storage (ticker, date, close_price, created_at)
- **dividend_data**: Dividend payments storage (ticker, date, dividend_amount, created_at)
- **dividend_coverage**: Coverage tracking for periods checked (ticker, start_date, end_date, has_dividends, created_at)

#### Performance Characteristics
- **First Call**: Normal speed (fetches from Yahoo, stores in warehouse)
- **Subsequent Calls**: 100x+ faster (served from warehouse cache)
- **Dividend Data**: 542x faster on repeated calls
- **Memory Efficient**: Embedded SQLite with WAL mode
- **Zero Repeated API Calls**: Once a period is checked, no more Yahoo calls

## 🎨 Presentation Layer

The presentation layer handles user interaction and coordinates with the application layer. The application now supports multiple presentation interfaces: CLI (command-line) and Web (React frontend).

### CLI Interface (Legacy)

#### MainMenu
- **Purpose**: Interactive command-line interface
- **Features**:
  - User-friendly menu system
  - Error handling and user feedback
  - Graceful interruption handling
  - Clear visual formatting

#### PortfolioController
- **Purpose**: Orchestrates user interactions with use cases
- **Responsibilities**:
  - Coordinate between UI and use cases
  - Handle user input validation
  - Format and display results
  - Manage application state (current portfolio)

### Web Interface (React Frontend)

#### Component Architecture
The React frontend follows a component-based architecture with clear separation of concerns:

```
frontend/src/
├── components/           # Reusable UI components
│   ├── common/          # Common UI components
│   ├── layout/          # Layout components (Header, Sidebar, MainLayout)
│   └── portfolio/       # Portfolio-specific components
├── pages/               # Page-level components
├── services/            # API service layer
├── types/               # TypeScript type definitions
└── utils/               # Utility functions
```

#### Key Components

##### PortfolioUpload Component
- **Purpose**: Handles CSV file upload with drag-and-drop functionality
- **Features**:
  - File validation (CSV format only)
  - Drag and drop interface
  - Upload progress indicators
  - Error handling and user feedback
- **Props**:
  - `onUploadSuccess`: Callback for successful upload
  - `onUploadError`: Callback for upload errors

##### PortfolioTable Component
- **Purpose**: Displays portfolio data in tabular format
- **Features**:
  - Responsive table design
  - Clean data presentation
  - Action buttons (clear, refresh)
- **Props**:
  - `portfolio`: Portfolio data to display
  - `onClear`: Callback for clear action
  - `onRefresh`: Callback for refresh action

##### MainLayout Component
- **Purpose**: Main application layout wrapper
- **Features**:
  - Header with navigation
  - Sidebar for additional controls
  - Responsive design
  - Consistent styling

#### API Service Layer

##### ApiService Class
- **Purpose**: Centralized API communication
- **Features**:
  - Axios-based HTTP client
  - Request/response interceptors
  - Error handling and transformation
  - Type-safe API calls
- **Methods**:
  - `uploadPortfolio()`: Upload CSV file
  - `getPortfolio()`: Retrieve current portfolio
  - `clearPortfolio()`: Clear portfolio data
  - `analyzePortfolio()`: Analyze portfolio (placeholder)
  - `analyzeTickers()`: Analyze individual tickers (placeholder)

#### Type Safety
- **TypeScript Integration**: Full type safety from API to UI
- **API Types**: Comprehensive type definitions for all API responses
- **Component Props**: Typed component props and state
- **Error Handling**: Typed error objects with proper error boundaries

### FastAPI Backend Integration

#### REST API Endpoints
The backend exposes a comprehensive REST API for frontend integration:

```python
# API Endpoints
@app.get("/health")                    # Health check
@app.post("/portfolio/upload")         # Upload portfolio CSV
@app.get("/portfolio")                 # Get current portfolio
@app.delete("/portfolio")              # Clear portfolio
@app.get("/portfolio/analysis")        # Analyze portfolio
@app.get("/portfolio/tickers/analysis") # Analyze tickers
```

#### CORS Configuration
- **Cross-Origin Support**: Proper CORS setup for frontend-backend communication
- **Allowed Origins**: Localhost development and production domains
- **Credentials**: Support for authenticated requests
- **Methods**: Full HTTP method support

#### File Upload Handling
- **Multipart Support**: Handles CSV file uploads
- **Temporary Storage**: Secure temporary file management
- **Validation**: File type and format validation
- **Cleanup**: Automatic cleanup of temporary files

#### Error Handling
- **HTTP Status Codes**: Proper HTTP status code responses
- **Error Messages**: User-friendly error messages
- **Validation Errors**: Detailed validation error responses
- **Exception Handling**: Comprehensive exception handling

### State Management

#### Frontend State
- **React Hooks**: useState and useEffect for local state management
- **Component State**: Local state for UI interactions
- **API State**: Loading, error, and success states
- **Portfolio State**: Current portfolio data management

#### Backend State
- **Global State**: Current portfolio stored in memory
- **Session Management**: Portfolio persistence across requests
- **Dependency Injection**: Controller instances managed globally

### User Interaction Flow

#### Web Interface Flow
```
User Action → React Component → API Service → FastAPI Endpoint → Use Case → Repository
     ↓              ↓              ↓              ↓              ↓
UI Update ← Component State ← API Response ← HTTP Response ← Business Logic ← Data Source
```

#### CLI Interface Flow (Legacy)
```
User Input → Menu → Controller → Use Case → Repository → External System
     ↓           ↓        ↓           ↓
Response ← Display ← Response ← Data ← API Response
```

### Responsive Design

#### Mobile-First Approach
- **Tailwind CSS**: Utility-first CSS framework
- **Responsive Breakpoints**: Mobile, tablet, and desktop layouts
- **Flexible Grid**: Responsive grid system
- **Touch-Friendly**: Mobile-optimized interactions

#### Component Responsiveness
- **Portfolio Table**: Responsive table with horizontal scroll on mobile
- **Upload Interface**: Touch-friendly drag and drop
- **Navigation**: Collapsible sidebar for mobile
- **Forms**: Mobile-optimized form inputs

### Development Experience

#### Hot Reloading
- **Frontend**: Vite development server with instant updates
- **Backend**: Uvicorn with auto-reload on code changes
- **Full-Stack**: Both services restart automatically on changes

#### Development Tools
- **TypeScript**: Compile-time type checking
- **ESLint**: Code quality and style enforcement
- **Vite**: Fast build tool and development server
- **FastAPI Docs**: Automatic API documentation at `/docs`

#### Local Development
- **Single Command**: `./local/run.sh start` starts both services
- **Port Management**: Automatic port conflict resolution
- **Process Management**: Graceful start/stop of all services
- **Status Monitoring**: Real-time service status checking

## 🔄 Data Flow

### Portfolio Loading Flow (Web Interface)
```
1. User drags CSV file to PortfolioUpload component
2. File validation and upload to /portfolio/upload endpoint
3. FastAPI processes file and loads portfolio using LoadPortfolioUseCase
4. Portfolio stored in backend memory and returned to frontend
5. PortfolioTable component displays portfolio data
6. User can clear portfolio or upload new file
```

### Portfolio Loading Flow (CLI Interface)
```
1. User selects "Load Portfolio" from menu
2. PortfolioController.load_portfolio() [LOGGED: User action]
3. LoadPortfolioUseCase.execute(LoadPortfolioRequest) [LOGGED: Business operation]
4. CsvPortfolioRepository.load(file_path) [LOGGED: File operation]
5. Parse CSV → Create Ticker/Position objects → Create Portfolio [LOGGED: Domain operations]
6. Return LoadPortfolioResponse with success/error [LOGGED: Performance metrics]
7. Controller displays result to user [LOGGED: User action completion]
```

### Portfolio Analysis Flow (Web Interface)
```
1. User clicks "Analyze Portfolio" button
2. Frontend calls /portfolio/analysis endpoint
3. FastAPI processes request using AnalyzePortfolioUseCase
4. Market data fetched from YFinanceMarketRepository or WarehouseMarketRepository
5. Analysis results returned to frontend
6. Frontend displays results in appropriate UI components
```

### Portfolio Analysis Flow (CLI Interface)
```
1. User selects "Analyze Portfolio" [LOGGED: User action]
2. PortfolioController.analyze_portfolio() [LOGGED: User action]
3. Get date range from user input [LOGGED: User input]
4. AnalyzePortfolioUseCase.execute(AnalyzePortfolioRequest) [LOGGED: Business operation]
5. YFinanceMarketRepository.get_price_history() [LOGGED: API call with timing]
6. Calculate portfolio metrics using domain objects [LOGGED: Calculations and performance]
7. Return AnalyzePortfolioResponse with metrics [LOGGED: Business operation completion]
8. Controller formats and displays results [LOGGED: User action completion]
```


## 🔍 Data Validation & Quality Assurance

### Missing Data Detection System

The application includes comprehensive data validation to ensure analysis accuracy and provide clear feedback about data availability issues.

#### Portfolio-Level Data Validation

**Purpose**: Identify and report tickers with missing or incomplete data for portfolio analysis.

**Implementation**:
- **Missing Tickers Detection**: Identifies tickers with no data available at all
- **Start Date Validation**: Detects tickers without data at analysis start date
- **Business Day Tolerance**: 5-day tolerance accounts for weekends, holidays, and data delays
- **User-Friendly Reporting**: Clear warnings about data availability issues

**Response Structure**:
```python
@dataclass
class AnalyzePortfolioResponse:
    metrics: Optional[PortfolioMetrics]
    success: bool
    message: str
    missing_tickers: List[str] = None
    tickers_without_start_data: List[str] = None
```

#### Ticker-Level Data Validation

**Purpose**: Validate individual ticker data availability with detailed reporting.

**Implementation**:
- **Start Date Check**: Validates data availability at analysis start date
- **First Available Date**: Reports when data first becomes available
- **Tolerance Handling**: Uses business day tolerance for realistic validation

**Response Structure**:
```python
@dataclass
class AnalyzeTickerResponse:
    metrics: Optional[TickerMetrics]
    success: bool
    message: str
    has_data_at_start: bool = True
    first_available_date: Optional[str] = None
```

#### User Experience

**Data Issues Display**:
```
⚠️  DATA AVAILABILITY ISSUES
============================================================
❌ No data available for: INVALID
   These tickers will be excluded from analysis.

⚠️  No data at start date for: TSLA, NVDA
   These tickers may have incomplete analysis periods.
   Consider adjusting your start date or excluding these tickers.
============================================================
```

**Benefits**:
- **Analysis Accuracy**: Prevents misleading results from incomplete data
- **User Awareness**: Clear understanding of data limitations
- **Informed Decisions**: Users can adjust analysis parameters accordingly
- **Transparency**: Full visibility into data availability issues

## 🎨 Color-Coded Metrics System

### Overview
The application includes a comprehensive color-coding system that provides instant visual feedback on metric performance based on predefined thresholds from METRICS_MEMORANDUM.md.

### Architecture Components

#### MetricsColorService Interface
**Location**: `src/application/interfaces/metrics_color_service.py`

**Purpose**: Defines the contract for color-coding financial metrics.

**Key Methods**:
- `get_color_for_metric()`: Returns color code for specific metric values
- `get_level_for_metric()`: Returns performance level (Bad/Normal/Excellent)
- `colorize_text()`: Applies color to text strings
- `colorize_percentage()`: Colorizes percentage values
- `colorize_ratio()`: Colorizes ratio values

#### ColorMetricsService Implementation
**Location**: `src/infrastructure/color_metrics_service.py`

**Purpose**: Concrete implementation of color-coding service with context-aware thresholds.

**Features**:
- **Context-Aware Thresholds**: Different rules for portfolio vs ticker metrics
- **Special Metric Handling**: Proper logic for metrics where lower values are better
- **ANSI Color Support**: Full terminal color compatibility
- **Extensible Design**: Easy addition of new metrics and thresholds

#### TableFormatter Utility
**Location**: `src/infrastructure/table_formatter.py`

**Purpose**: Advanced table formatting that properly handles ANSI color codes.

**Key Features**:
- **ANSI Code Stripping**: Removes color codes for width calculations
- **Dynamic Column Sizing**: Automatic width calculation based on content
- **Proper Alignment**: Centers content while accounting for color codes
- **Flexible Formatting**: Supports various table layouts and separators

### Color Coding Thresholds

#### Portfolio Metrics (Consolidated)
- **Total Return**: Red <10%, Yellow 10-30%, Green >30%
- **Annualized Return**: Red <5%, Yellow 5-15%, Green >15%
- **Sharpe Ratio**: Red <0.5, Yellow 0.5-1.5, Green >1.5
- **Sortino Ratio**: Red <1.0, Yellow 1.0-2.0, Green >2.0
- **Calmar Ratio**: Red <0.5, Yellow 0.5-1.0, Green >1.0
- **Max Drawdown**: Red >-30%, Yellow -30% to -15%, Green >-15%
- **Volatility**: Red >20%, Yellow 10-20%, Green <10%
- **VaR (95%)**: Red >-2%, Yellow -2% to -1%, Green >-1%
- **Beta**: Red >1.3, Yellow 0.7-1.3, Green <0.7

#### Ticker Metrics (Individual)
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

### Display Format Options

#### Cards Format
- **Purpose**: Detailed individual display for each ticker
- **Features**: Comprehensive metrics with color coding
- **Use Case**: Detailed analysis and comparison

#### Table Format
- **Purpose**: Compact tabular display of all tickers
- **Features**: Color-coded metrics in organized columns
- **Use Case**: Quick overview and comparison

### Integration Points

#### PortfolioController Integration
- **Dependency Injection**: Color service injected into controller
- **Display Methods**: All display methods use color service
- **Format Selection**: Users can choose between cards and table formats

#### SOLID Principles Compliance
- **Single Responsibility**: Color service has single responsibility
- **Open/Closed**: Extensible for new metrics and thresholds
- **Dependency Inversion**: Controller depends on color service abstraction

## 🧪 Testing Strategy

### Test Pyramid

#### Unit Tests (34 tests)
- **Scope**: Individual classes and methods
- **Focus**: Domain entities and value objects
- **Isolation**: No external dependencies
- **Coverage**: 100% for domain layer

#### Integration Tests (4 tests)
- **Scope**: Multiple components working together
- **Focus**: Use cases with real repositories
- **External**: Limited external API calls
- **Validation**: End-to-end workflows

#### E2E Tests (Future)
- **Scope**: Full application scenarios
- **Focus**: User workflows through CLI
- **Environment**: Real data and APIs

### Test Structure
```python
# Unit Test Example
class TestTicker:
    def test_creation_with_valid_symbol(self):
        ticker = Ticker("AAPL")
        assert ticker.symbol == "AAPL"
    
    def test_empty_symbol_raises_error(self):
        with pytest.raises(ValueError):
            Ticker("")

# Integration Test Example
class TestPortfolioAnalysisIntegration:
    def test_complete_portfolio_workflow(self):
        # Load portfolio
        # Analyze portfolio
        # Verify results
```

## 🔗 Dependency Management

### Dependency Injection

The application uses manual dependency injection in `main.py`:

```python
def setup_dependencies():
    # Infrastructure
    portfolio_repo = CsvPortfolioRepository()
    market_repo = YFinanceMarketRepository()
    
    # Application
    load_use_case = LoadPortfolioUseCase(portfolio_repo)
    analyze_use_case = AnalyzePortfolioUseCase(market_repo)
    
    # Presentation
    controller = PortfolioController(load_use_case, analyze_use_case)
    
    return controller
```

### Dependency Flow
```
Presentation → Application → Domain
     ↓              ↓
Infrastructure ← Interfaces
```

## 🚀 Extensibility

### Adding New Data Sources
1. Implement new repository (e.g., `BloombergMarketRepository`)
2. Register in dependency injection
3. No changes needed in use cases or presentation

### Adding New Analysis Methods
1. Create new use case (e.g., `CalculateVaRUseCase`)
2. Add controller method
3. Add menu option
4. Domain objects remain unchanged

### Adding New Interfaces
1. Create new presentation layer (e.g., `WebController`)
2. Reuse existing use cases
3. No changes to business logic

## 📊 Performance Considerations

### Efficiency Features
- **Lazy Loading**: Data fetched only when needed
- **Caching**: Results cached within request scope
- **Batch Operations**: Multiple tickers fetched in single API call
- **Memory Management**: Proper resource cleanup

### Scalability
- **Stateless Services**: Use cases are stateless
- **Repository Pattern**: Easy to swap data sources
- **Async Ready**: Architecture supports async operations

## 🔐 Error Handling

### Error Strategy
- **Domain Errors**: Business rule violations (ValueError)
- **Application Errors**: Use case failures (structured responses)
- **Infrastructure Errors**: External system failures (wrapped)
- **Presentation Errors**: User-friendly messages

### Error Flow
```
External Error → Repository → Use Case → Controller → User Message
                     ↓           ↓           ↓
                  Log Error → Structure → Format → Display
```

## 🎯 Design Patterns Used

1. **Repository Pattern**: Data access abstraction
2. **Use Case Pattern**: Business logic encapsulation
3. **Request/Response Pattern**: Consistent interface design
4. **Factory Pattern**: Object creation (implicit in repositories)
5. **Strategy Pattern**: Different analysis strategies
6. **Aggregate Pattern**: Portfolio as aggregate root
7. **Value Object Pattern**: Immutable domain values
8. **Singleton Pattern**: LoggerService for centralized logging
9. **Decorator Pattern**: Logging decorators for cross-cutting concerns
10. **Observer Pattern**: Logging as observation of system events

## 🔮 Future Enhancements

### Planned Features
- **Web Interface**: REST API and web dashboard
- **Database Support**: PostgreSQL/SQLite repositories
- **Real-time Data**: WebSocket market data feeds
- **Advanced Analytics**: Machine learning models
- **Portfolio Optimization**: Mean reversion, momentum strategies
- **Risk Management**: Advanced VaR calculations, stress testing

### Architecture Readiness
The current architecture is designed to support these enhancements without major structural changes:
- New repositories can be added easily
- New use cases follow established patterns
- Multiple presentation layers can coexist
- Domain model is rich enough for complex scenarios

---

*This architecture documentation reflects version 4.2.0 of the Portfolio Analysis Tool with full-stack implementation featuring FastAPI backend and React frontend.*
