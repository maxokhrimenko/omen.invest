# 🏗️ Architecture Documentation

## Overview

The Portfolio Analysis Tool has been completely refactored to follow **Clean Architecture** principles, ensuring separation of concerns, testability, and maintainability. This document provides a comprehensive overview of the application's architecture, design patterns, and data flow.

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
│   │   │   └── yfinance_market_repository.py # Market data from yfinance
│   │   ├── services/              # External service integrations
│   │   │   └── __init__.py
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
- **Output**: `AnalyzePortfolioResponse` (metrics, success, message)
- **Responsibilities**:
  - Fetch market data for all portfolio tickers
  - Calculate portfolio-level metrics
  - Handle missing data scenarios
- **Calculated Metrics**:
  - Total return, annualized return
  - Volatility, Sharpe ratio, Sortino ratio
  - Maximum drawdown, Calmar ratio
  - Value at Risk (VaR), Beta

#### AnalyzeTickerUseCase
- **Input**: `AnalyzeTickerRequest` (ticker, date range, risk-free rate)
- **Output**: `AnalyzeTickerResponse` (metrics, success, message)
- **Responsibilities**:
  - Fetch price and dividend data for single ticker
  - Calculate individual ticker metrics
  - Handle ticker-specific errors

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

### Configuration Management

#### Settings Service
- **Purpose**: Centralized configuration management
- **Features**:
  - YAML-based configuration
  - Default fallbacks
  - Type-safe access methods
  - Environment-specific settings

## 🎨 Presentation Layer

The presentation layer handles user interaction and coordinates with the application layer.

### CLI Interface

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

### User Interaction Flow

```
User Input → Menu → Controller → Use Case → Repository → External System
                  ↓                ↓           ↓
                Response ← Response ← Data ← API Response
```

## 🔄 Data Flow

### Portfolio Loading Flow
```
1. User selects "Load Portfolio"
2. PortfolioController.load_portfolio()
3. LoadPortfolioUseCase.execute(LoadPortfolioRequest)
4. CsvPortfolioRepository.load(file_path)
5. Parse CSV → Create Ticker/Position objects → Create Portfolio
6. Return LoadPortfolioResponse with success/error
7. Controller displays result to user
```

### Portfolio Analysis Flow
```
1. User selects "Analyze Portfolio"
2. PortfolioController.analyze_portfolio()
3. Get date range from user input
4. AnalyzePortfolioUseCase.execute(AnalyzePortfolioRequest)
5. YFinanceMarketRepository.get_price_history()
6. Calculate portfolio metrics using domain objects
7. Return AnalyzePortfolioResponse with metrics
8. Controller formats and displays results
```

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

*This architecture documentation reflects version 4.0.0 of the Portfolio Analysis Tool.*
