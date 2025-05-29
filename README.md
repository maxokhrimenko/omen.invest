# 📈 Investment Portfolio Analysis Tool

A comprehensive Python-based tool for analyzing investment portfolios, providing both consolidated portfolio metrics and detailed per-ticker analysis.

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

## 📁 Project Structure

### `portfolio_analysis_consolidated.py`
The core file handling overall portfolio analysis and shared utilities.

**Key Components:**
- Portfolio data parsing
- Price data loading and validation
- Common utility functions
- Aggregate portfolio metrics calculation
- Data validation and error handling

**Main Functions:**
- `parse_portfolio()`: Converts raw portfolio text to structured data
- `load_prices()`: Downloads historical price data
- `sharpe_ratio()`: Calculates risk-adjusted returns
- `max_drawdown()`: Computes maximum portfolio drawdown
- `do_aggregate()`: Performs overall portfolio analysis

### `portfolio_analysis_by_one.py`
Handles detailed analysis of individual stocks.

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
Current version: 3.1.0

## Features
- Portfolio analysis with consolidated metrics
- Per-ticker analysis with dividend tracking
- Color-coded yield indicators
- CSV-based portfolio data input
- Comprehensive error handling

## Requirements
- Python 3.6+
- pandas
- colorama

## Installation
1. Clone the repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage
1. Place your portfolio data in `input/input.csv` with the following format:
```csv
ticker,shares,price
AAPL,10,150.00
MSFT,5,300.00
```

2. Run the analysis:
```bash
# For consolidated analysis
python portfolio_analysis_consolidated.py

# For per-ticker analysis
python portfolio_analysis_by_one.py
```

## Output
The tool provides:
- Total portfolio value
- Per-ticker metrics
- Dividend yields with color coding
- Position sizes and weights
- Error handling for missing data

## File Structure
- `portfolio_analysis_consolidated.py`: Consolidated portfolio analysis
- `portfolio_analysis_by_one.py`: Per-ticker analysis
- `input/input.csv`: Portfolio data file
- `README.md`: This documentation
- `CHANGELOG.md`: Version history
- `.gitignore`: Git ignore rules

## Error Handling
The tool includes comprehensive error handling for:
- Missing input files
- Invalid CSV format
- Missing price data
- Invalid numeric values

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details. 