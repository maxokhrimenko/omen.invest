# 📈 Altidus - Investment Portfolio Analysis Tool

A comprehensive full-stack application for analyzing investment portfolios, built with clean architecture principles. The system consists of a FastAPI backend with clean architecture, a React frontend interface, and a robust database layer.

> **🚀 Version 4.4.9 - Portfolio Dividend Metrics & Frontend Chart Enhancement**: This release introduces comprehensive portfolio-level dividend metrics and completes the CLI-frontend alignment, ensuring consistent behavior across all interfaces with enhanced visual presentation and custom chart legends.

## 🏗️ Architecture Overview

The application is structured as a full-stack service with clear component separation:

- **Backend** (`/backend/`): FastAPI-based REST API with Clean Architecture
- **Frontend** (`/frontend/`): React + TypeScript web interface
- **Database** (`/database/`): SQLite warehouse with caching and data storage
- **Shared** (`/shared/`): Common types, schemas, and utilities
- **Documentation** (`/docs/`): Comprehensive technical documentation

## 🎯 Overview

This tool helps investors analyze their portfolios by providing:
- Overall portfolio performance metrics with color-coded indicators
- Individual stock analysis with dividend tracking
- Risk-adjusted return calculations with visual performance feedback
- Multiple display formats (cards and table views)
- Professional color-coded output based on performance thresholds

## 📋 Features

### 🚀 Parallel Processing & Warehouse Optimization (NEW in v4.4.3)
- **Parallel Calculation Service**: Multi-threaded financial calculations with intelligent worker management (3-5x faster)
- **Parallel Data Fetcher**: Concurrent data fetching for warehouse operations and external API calls (2-4x faster)
- **Warehouse Optimizer**: Database optimization with connection pooling and query performance enhancements (50%+ improvement)
- **Smart Worker Allocation**: Dynamic worker count calculation based on task type (CPU-bound vs I/O-bound)
- **Error Isolation**: Comprehensive error handling with task-level isolation to prevent cascade failures
- **Database Performance Tuning**: Automatic optimization with WAL mode, cache settings, and performance indexes

### 🎯 Enhanced Data Validation & Analysis Accuracy (v4.4.1)
- **Smart Data Validation**: Dynamic date range validation that considers the actual analysis period instead of fixed assumptions
- **Adaptive Coverage Thresholds**: Different coverage requirements based on analysis period length (more lenient for shorter periods)
- **End Date Integration**: Data validation now properly considers both start and end dates for accurate coverage calculations
- **Trading Day Estimation**: Intelligent estimation of expected trading days based on actual date range (70% of calendar days)
- **Flexible Tolerance System**: 5-day business day tolerance for start date validation to account for weekends and holidays
- **Period-Aware Validation**: Coverage thresholds adapt based on analysis period length for more accurate analysis

### 🚀 Enhanced Frontend Architecture & Logging System (v4.4.0)
- **Interactive Charts**: Recharts-based performance comparison charts with hover effects and tooltips
- **Benchmark Comparisons**: Side-by-side portfolio vs S&P 500 vs NASDAQ performance visualization
- **Advanced Risk Metrics**: VaR (Value at Risk) and Beta calculations with color-coded indicators
- **Time Series Data**: Historical portfolio value tracking with benchmark overlays
- **Enhanced Frontend Logging**: UUID-based portfolio session tracking with comprehensive logging
- **Responsive Chart Design**: Mobile-friendly chart components with proper scaling

### 🌐 Full-Stack Web Application (v4.2.0)
- **Modern Web Interface**: React + TypeScript frontend with responsive design
- **REST API Backend**: FastAPI-based backend with comprehensive endpoints
- **Drag & Drop Upload**: Intuitive CSV file upload with validation
- **Real-time Feedback**: Immediate visual feedback for all operations
- **Mobile Responsive**: Works seamlessly on desktop and mobile devices
- **Type Safety**: End-to-end TypeScript integration from API to UI
- **Hot Reloading**: Instant development feedback for both frontend and backend

### 🎯 Annualized Dividend Calculation System (v4.1.1)
- **Automatic Frequency Detection**: Intelligently detects dividend payment patterns (Monthly, Quarterly, Semi-Annual, Annual, Irregular)
- **Smart Annualization**: Calculates proper annualized dividends based on detected payment frequency
- **Enhanced Display**: New table columns showing annualized dividend amount, yield, and payment frequency
- **Frequency Color Coding**: Visual indicators for different payment frequencies (🟢 Monthly, 🔵 Quarterly, 🟡 Semi-Annual, 🟠 Annual, 🔴 Irregular)
- **Accurate Yield Calculation**: Uses average price over analysis period for consistent yield calculations
- **Comparable Metrics**: All dividend yields are now properly annualized for fair comparison across all stocks

### 🏪 Warehouse System (v4.1.0)
- **Read-Through Caching**: Transparent SQLite-based caching layer for market data
- **Dividend Absence Caching**: Stores information about periods with no dividends to prevent repeated API calls
- **Trading-Day Awareness**: Smart gap filling that only fetches missing trading days
- **Massive Performance Gains**: 100x+ faster on subsequent requests
- **Feature Flag Support**: `WAREHOUSE_ENABLED` for instant rollback capability
- **Comprehensive Observability**: Real-time metrics and performance monitoring
- **Zero Repeated API Calls**: Once a period is checked, no more Yahoo calls

### Portfolio-Level Analysis
- Total portfolio value tracking with time series visualization
- Overall return calculation with color-coded performance indicators
- Annualized return computation with visual feedback
- Sharpe ratio calculation with performance thresholds
- Maximum drawdown analysis with risk indicators
- **VaR (Value at Risk) calculation** with 95% confidence level
- **Beta calculation** against S&P 500 benchmark
- **Benchmark comparisons** with S&P 500 and NASDAQ
- Trading days tracking
- **Missing data detection and validation**
- **Color-coded metrics based on METRICS_MEMORANDUM.md thresholds**

### Per-Ticker Analysis
- Individual stock performance metrics with color coding
- Dividend yield tracking and analysis with visual indicators
- **Multiple display formats**: Cards (detailed) and Table (compact) views
- **Interactive ticker analysis** with collapsible details and charts
- Historical dividend data analysis
- Expected dividend calculations
- **VaR and Beta calculations** for individual tickers
- Risk metrics per ticker with performance color coding
- **Data availability validation with business day tolerance**
- **Context-aware color coding**: Different thresholds for portfolio vs ticker metrics

### Data Validation & Quality Assurance
- **Missing Data Detection**: Identifies tickers with no data available
- **Start Date Validation**: Detects tickers without data at analysis start date (5-day business tolerance)
- **User-Friendly Warnings**: Clear messages about data availability issues
- **Analysis Impact Reporting**: Shows how missing data affects analysis accuracy
- **Transparent Reporting**: Full visibility into data limitations and recommendations

### Color-Coded Metrics System
- **Performance-Based Color Coding**: Red (Bad), Yellow (Normal), Green (Excellent)
- **Context-Aware Thresholds**: Different color rules for portfolio vs individual ticker metrics
- **Comprehensive Coverage**: All financial metrics color-coded based on METRICS_MEMORANDUM.md
- **Visual Performance Feedback**: Instant visual assessment of metric performance
- **Professional Presentation**: Clean, readable output with color-coded insights
- **Terminal Compatible**: Full ANSI color code support for most terminals

### Display Format Options
- **Cards Format**: Detailed individual cards for each ticker with comprehensive metrics
- **Table Format**: Compact table view with all tickers in rows and metrics in columns
- **Format Selection**: Users can choose their preferred display format
- **Proper Alignment**: Advanced table formatting that handles color codes correctly
- **Dynamic Sizing**: Automatic column width calculation based on content

### Comprehensive Logging System
- **Session-based logging**: Complete logs for each application session
- **Frontend logging**: UUID-based portfolio session tracking with individual log files
- **Dual log streams**: Session-specific and total application logs
- **Detailed operation tracking**: User actions, API calls, file operations, business operations
- **Performance monitoring**: Timing information for all operations
- **Human-readable format**: Easy debugging and analysis
- **Log management**: Administrative tools for log cleanup and statistics
- **Enhanced debugging**: Comprehensive frontend operation logging

## 🏗️ Architecture

This application follows **Clean Architecture** principles with clear separation of concerns:

### 📦 Project Structure

```
omen.invest/
├── backend/                    # Backend API and Services
│   ├── src/                   # Backend source code
│   │   ├── domain/            # Domain layer (Clean Architecture)
│   │   ├── application/       # Application layer
│   │   ├── infrastructure/    # Infrastructure layer
│   │   └── presentation/      # Presentation layer
│   ├── tests/                 # Backend tests
│   ├── admin/                 # Administrative tools
│   ├── logs/                  # Backend logs
│   ├── main.py                # Backend entry point
│   └── requirements.txt       # Backend dependencies
├── frontend/                  # Frontend Application (Planned)
│   ├── src/                   # Frontend source code
│   ├── public/                # Public static files
│   ├── tests/                 # Frontend tests
│   └── package.json           # Frontend dependencies
├── database/                  # Database and Data Storage
│   ├── warehouse/             # SQLite warehouse database
│   ├── migrations/            # Database migrations (Future)
│   └── seeds/                 # Database seeds (Future)
├── shared/                    # Shared Resources
│   ├── types/                 # Shared TypeScript types
│   ├── schemas/               # API schemas and contracts
│   ├── utils/                 # Shared utility functions
│   └── constants/             # Shared constants
├── docs/                      # Documentation
│   ├── AI.MD                  # AI/LLM documentation
│   ├── ARCHITECTURE.md        # Technical architecture
│   ├── METRICS_MEMORANDUM.md  # Financial metrics definitions
│   └── structure.md           # Repository structure
├── scripts/                   # Build and deployment scripts
├── input/                     # Input data files
├── config/                    # Configuration files
└── README.md                  # Main project documentation
```

### 🎯 Key Benefits of This Architecture

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Dependency Inversion**: Business logic doesn't depend on external libraries
3. **Testability**: Easy to unit test with comprehensive test coverage
4. **Maintainability**: Changes in one layer don't affect others
5. **Extensibility**: Easy to add new features or change implementations

### Legacy Files (Preserved for Reference)

- `portfolio_analysis_consolidated.py`: Original consolidated analysis
- `portfolio_analysis_by_one.py`: Original per-ticker analysis

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Internet connection for market data

### Quick Start (Full-Stack)

1. **Setup the entire application**:
   ```bash
   ./local/run.sh setup
   ```

2. **Start both backend and frontend**:
   ```bash
   ./local/run.sh start
   ```

3. **Access the application**:
   - **Web Interface**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **Backend API**: http://localhost:8000

### Backend Installation (CLI Mode)

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Backend Usage (CLI Mode)

1. **Prepare your portfolio** in `input/test.csv` with the following format:
   ```csv
   ticker,position
   AAPL,10
   MSFT,5
   GOOGL,3
   ```

2. **Run the interactive application**:
   ```bash
   cd backend
   python main.py
   ```

3. **Follow the interactive menu** to:
   - Load your portfolio
   - Analyze portfolio performance  
   - Analyze individual tickers
   - Compare ticker performance
   - Generate comprehensive reports

### Frontend Usage (Web Interface)

1. **Start the frontend development server**:
   ```bash
   ./local/run.sh frontend
   ```

2. **Open your browser** to http://localhost:3000

3. **Upload your portfolio**:
   - Drag and drop a CSV file or click to select
   - View your portfolio data in a clean table format
   - Clear portfolio when needed

### API Usage

The backend provides a REST API for programmatic access:

```bash
# Health check
curl http://localhost:8000/health

# Upload portfolio
curl -X POST -F "file=@portfolio.csv" http://localhost:8000/portfolio/upload

# Get current portfolio
curl http://localhost:8000/portfolio

# Clear portfolio
curl -X DELETE http://localhost:8000/portfolio
```

### Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests  
pytest tests/integration/
```

### Log Management

The application includes comprehensive logging with administrative tools:

```bash
# View log statistics
python admin/logs_clear.py --stats

# Clear session logs
python admin/logs_clear.py --clear-sessions --force

# Clear all logs
python admin/logs_clear.py --clear-all --force

# Backup and clear logs
python admin/logs_clear.py --backup-and-clear --force
```

**Log Structure:**
- `logs/sessions/` - Complete logs for each application session
- `logs/total/` - All logs across all sessions
- Human-readable format with detailed timing and operation tracking

### Legacy Scripts (Still Available)

For backwards compatibility, the original scripts are still available:

**Key Components:**
- Per-ticker performance metrics
- Dividend analysis
- Yield calculations
- Color-coded output formatting

**Main Functions:**
- `get_yield_color()`: Determines color coding for yield values
- `get_annual_dividends_and_yields()`: Calculates dividend metrics
- `do_per_ticker()`: Performs individual stock analysis

## 🛠️ Technical Details

### Dependencies

#### Backend
- Python 3.8+
- FastAPI
- Uvicorn
- pandas
- numpy
- yfinance
- pydantic
- python-multipart

#### Frontend
- Node.js 18+
- React 19
- TypeScript
- Vite
- Tailwind CSS
- Axios
- Lucide React
- React Router

### Data Sources
- Yahoo Finance API (via yfinance)
- Real-time market data
- Historical price data
- Dividend history

### Configuration
- Portfolio data in `RAW_PORTFOLIO`
- Analysis period in `START` and `END`
- Risk-free rate in `RF_ANNUAL`

## 📊 Output Format

### Portfolio Analysis
```
📊 PORTFOLIO RESULTS
🗓  [Start Date] → [End Date] ([Trading Days])
💸  Start:    $[Value]
💰  End:      $[Value]
🔺/🔻  Return:    [Percentage]
📈  Annual:   [Percentage]
📏  Sharpe:   [Value]
📉  MaxDD:    [Percentage]

⚠️  DATA AVAILABILITY ISSUES
============================================================
❌ No data available for: INVALID
   These tickers will be excluded from analysis.

⚠️  No data at start date for: TSLA, NVDA
   These tickers may have incomplete analysis periods.
   Consider adjusting your start date or excluding these tickers.
============================================================
```

### Per-Ticker Analysis
```
📑 PER-TICKER METRICS (Sharpe ↓)
[Formatted table with columns:]
- Ticker
- Start $
- End $
- TotRet
- AnnRet
- Volatility
- Sharpe
- MaxDD
- AnnDiv (Annualized Dividend)
- DivYield (Annualized Dividend Yield)
- Freq (Payment Frequency)
- Momentum
```

## 🚀 Usage

1. Configure your portfolio in `RAW_PORTFOLIO`
2. Set analysis period in `START` and `END`
3. Run either:
   - `portfolio_analysis_consolidated.py` for overall analysis
   - `portfolio_analysis_by_one.py` for detailed stock analysis

## 📝 Notes

- Dividend yields are color-coded:
  - 🔴 Red: < 2%
  - 🟡 Yellow: 2-6%
  - 🟢 Green: > 6%
- All calculations use adjusted prices
- Dividend calculations include expected future payments
- Maximum drawdown is calculated on a cumulative basis

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

## Version
Current version: 4.4.3 - **Portfolio Analysis & Visualization**

## Features
- **📊 Interactive Visualizations**: Recharts-based performance charts with benchmark comparisons
- **🎯 Advanced Risk Metrics**: VaR and Beta calculations with color-coded indicators
- **📈 Benchmark Analysis**: S&P 500 and NASDAQ comparison with time series data
- **🚀 Full-Stack Web Application**: Modern React frontend with FastAPI backend
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🎯 Annualized Dividend Calculation**: Smart frequency detection and proper annualization for fair comparison
- **🏪 Warehouse System**: Read-through caching with SQLite database for massive performance gains
- **📊 Dividend Absence Caching**: Intelligent caching that eliminates repeated API calls for periods with no dividends
- **⚡ Performance**: 100x+ faster on subsequent requests through intelligent caching
- **📈 Portfolio Analysis**: Consolidated metrics with color-coded performance indicators
- **🔍 Per-Ticker Analysis**: Individual analysis with dividend tracking and visual feedback
- **📋 Multiple Display Formats**: Cards (detailed) and table (compact) views
- **🎨 Color-Coded Metrics**: Comprehensive color-coding based on performance thresholds
- **📊 Advanced Table Formatting**: Proper color code handling and alignment
- **📁 CSV-Based Input**: Simple portfolio data input format with drag-and-drop upload
- **✅ Data Validation**: Comprehensive error handling and missing data detection
- **🔧 REST API**: Complete REST API for programmatic access
- **🎨 Modern UI**: Clean, intuitive web interface with real-time feedback
- **📝 Enhanced Logging**: UUID-based portfolio session tracking with comprehensive frontend logging

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed technical architecture documentation
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and changes
- **[METRICS_MEMORANDUM.md](METRICS_MEMORANDUM.md)**: Financial metrics definitions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Yahoo Finance for providing market data via the yfinance library
- The Python community for excellent financial analysis libraries 