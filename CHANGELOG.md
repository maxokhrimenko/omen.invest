# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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