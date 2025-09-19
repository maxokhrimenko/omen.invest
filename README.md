# 📈 Investment Portfolio Analysis Tool

A comprehensive Python-based tool for analyzing investment portfolios, built with clean architecture principles. Provides both consolidated portfolio metrics and detailed per-ticker analysis with an interactive CLI interface.

> **🚀 Recently Refactored**: This application has been completely refactored to follow SOLID principles and clean architecture patterns, making it more maintainable, testable, and extensible.

## 🎯 Overview

This tool helps investors analyze their portfolios by providing:
- Overall portfolio performance metrics
- Individual stock analysis with dividend tracking
- Risk-adjusted return calculations
- Dividend yield analysis with color-coded output

## 📋 Features

### Portfolio-Level Analysis
- Total portfolio value tracking
- Overall return calculation
- Annualized return computation
- Sharpe ratio calculation
- Maximum drawdown analysis
- Trading days tracking

### Per-Ticker Analysis
- Individual stock performance metrics
- Dividend yield tracking and analysis
- Color-coded yield indicators
- Historical dividend data analysis
- Expected dividend calculations
- Risk metrics per ticker

## 🏗️ Architecture

This application follows **Clean Architecture** principles with clear separation of concerns:

### 📦 Project Structure

```
src/
├── domain/                 # Business logic and rules
│   ├── entities/          # Core business objects
│   │   ├── ticker.py     # Ticker symbol entity
│   │   ├── position.py   # Position in portfolio
│   │   └── portfolio.py  # Portfolio aggregate
│   └── value_objects/     # Immutable value types
│       ├── money.py      # Money with currency
│       ├── percentage.py # Percentage values
│       └── date_range.py # Date range handling
├── application/           # Use cases and business workflows
│   ├── use_cases/        # Business use cases
│   │   ├── load_portfolio.py
│   │   ├── analyze_portfolio.py
│   │   ├── analyze_ticker.py
│   │   └── compare_tickers.py
│   └── interfaces/       # Repository interfaces
│       └── repositories.py
├── infrastructure/       # External concerns
│   ├── repositories/     # Data access implementations
│   │   ├── csv_portfolio_repository.py
│   │   └── yfinance_market_repository.py
│   └── config/          # Configuration management
│       └── settings.py
└── presentation/         # User interface
    ├── cli/             # Command-line interface
    │   └── menu.py
    └── controllers/     # Application controllers
        └── portfolio_controller.py

tests/
├── unit/                # Unit tests
└── integration/         # Integration tests

config/
└── settings.yaml       # Application configuration
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

### Installation

1. **Clone or download** this repository
2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. **Prepare your portfolio** in `input/input.csv` with the following format:
   ```csv
   ticker,position
   AAPL,10
   MSFT,5
   GOOGL,3
   ```

2. **Run the interactive application**:
   ```bash
   python main.py
   ```

3. **Follow the interactive menu** to:
   - Load your portfolio
   - Analyze portfolio performance  
   - Analyze individual tickers
   - Compare ticker performance
   - Generate comprehensive reports

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
- Python 3.x
- pandas
- numpy
- yfinance

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
- Sharpe
- MaxDD
- Max Yield
- Avg Yield
- Current Yield
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
Current version: 4.0.0 - **Major Refactoring Release**

## Features
- Portfolio analysis with consolidated metrics
- Per-ticker analysis with dividend tracking
- Color-coded yield indicators
- CSV-based portfolio data input
- Comprehensive error handling

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