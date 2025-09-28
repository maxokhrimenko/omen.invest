# 📊 Investment Metrics Memorandum

This document explains all metrics used in the portfolio analysis tool, their calculations, and thresholds.

*This metrics documentation reflects version 4.5.2 of the Portfolio Analysis Tool with frontend TypeScript improvements, code cleanup, enhanced type safety, and improved maintainability for better development experience.*

## 1. CONSOLIDATED PORTFOLIO METRICS

These metrics are calculated for the entire portfolio as a whole. The thresholds assume a multi-asset portfolio comparable with a balanced global 60/40 or similar. If your mandate is different, you may need to adjust the cut-offs.

### Return Metrics

#### Total Return
- **Calculation**: (End Value / Start Value) - 1
- **Thresholds**:
  - Bad: < 10%
  - Normal: 10% - 30%
  - Excellent: > 30%
- **Note**: For windows longer than 12 months, prefer using Annualised Return

#### Annualised Return
- **Calculation**: (1 + Total Return)^(252/trading_days) - 1
- **Thresholds**:
  - Bad: < 5%
  - Normal: 5% - 15%
  - Excellent: > 15%
- **Note**: 5% ≈ long-run "cash + inflation"; 15% beats equity indices

### Risk-Adjusted Return Metrics

#### Sharpe Ratio
- **Calculation**: √252 × (mean_daily_return - rf_daily) / std_daily_return
- **Thresholds**:
  - Bad: < 0.5
  - Normal: 0.5 - 1.5
  - Excellent: > 1.5
- **Note**: 1 ≈ "acceptable", 2+ is hedge-fund territory

#### Sortino Ratio
- **Calculation**: √252 × (mean_daily_return - rf_daily) / std_downside_return
- **Thresholds**:
  - Bad: < 1.0
  - Normal: 1.0 - 2.0
  - Excellent: > 2.0
- **Note**: Same intuition as Sharpe but focuses on downside volatility

#### Calmar Ratio
- **Calculation**: Annualised Return / |Max Drawdown|
- **Thresholds**:
  - Bad: < 0.5
  - Normal: 0.5 - 1.0
  - Excellent: > 1.0
- **Note**: >1 means the portfolio earns at least as fast as it falls

### Risk Metrics

#### Max Drawdown
- **Calculation**: min((current_value - running_max) / running_max)
- **Thresholds**:
  - Bad: > 30%
  - Normal: 15% - 30%
  - Excellent: < 15%
- **Note**: Smaller (closer to 0%) is better

#### Annualised Volatility
- **Calculation**: std_daily_return × √252
- **Thresholds**:
  - Bad: > 20%
  - Normal: 10% - 20%
  - Excellent: < 10%
- **Note**: 10% ≈ moderate-risk balanced fund

#### 1-day Parametric VaR (95%)
- **Calculation**: -(1.645 × std_daily_return - mean_daily_return) × 100
- **Thresholds**:
  - Bad: > 2.0%
  - Normal: 1.0% - 2.0%
  - Excellent: < 1.0%
- **Note**: Expressed as % of portfolio value

#### Beta vs Benchmark (SPY)
- **Calculation**: cov(portfolio_returns, benchmark_returns) / var(benchmark_returns)
- **Thresholds**:
  - Bad: > 1.3
  - Normal: 0.7 - 1.3
  - Excellent: < 0.7
- **Note**: < 0.7 implies defensive/diversifying stance

## 2. PER-TICKER METRICS

These metrics are calculated for individual securities. The cut-offs assume developed-market equities. For bonds/crypto/FX, you may need separate thresholds.

### Return Metrics

#### Annualised Return
- **Calculation**: Same as portfolio
- **Thresholds**:
  - Bad: < 5%
  - Normal: 5% - 20%
  - Excellent: > 20%
- **Note**: Green if it beats SPX handily

### Risk-Adjusted Return Metrics

#### Sharpe Ratio
- **Calculation**: Same as portfolio
- **Thresholds**: Same as portfolio

#### Sortino Ratio
- **Calculation**: Same as portfolio
- **Thresholds**:
  - Bad: < 0.8
  - Normal: 0.8 - 2.0
  - Excellent: > 2.0
- **Note**: Looser "yellow" band than portfolio

### Risk Metrics

#### Max Drawdown
- **Calculation**: Same as portfolio
- **Thresholds**:
  - Bad: > 50%
  - Normal: 30% - 50%
  - Excellent: < 30%
- **Note**: Single stocks swing wider than portfolios

#### Annualised Volatility
- **Calculation**: Same as portfolio
- **Thresholds**:
  - Bad: > 50%
  - Normal: 30% - 50%
  - Excellent: < 30%
- **Note**: 30% ≈ S&P constituents average

#### Beta to Portfolio
- **Calculation**: cov(ticker_returns, portfolio_returns) / var(portfolio_returns)
- **Thresholds**:
  - Bad: > 1.5
  - Normal: 0.5 - 1.5
  - Excellent: < 0.5
- **Note**: Low-beta names improve diversification

#### 1-day Historical VaR (95%)
- **Calculation**: 5th percentile of daily returns × 100
- **Thresholds**:
  - Bad: > 4%
  - Normal: 2% - 4%
  - Excellent: < 2%
- **Note**: Empirical 5th percentile of returns

### Momentum and Yield Metrics

#### 12-1 Momentum
- **Calculation**: (Price_21d_ago - Price_252d_ago) / Price_252d_ago
- **Thresholds**:
  - Bad: < 0%
  - Normal: 0% - 20%
  - Excellent: > 20%
- **Note**: Excludes last month to avoid reversal

#### Current Yield
- **Calculation**: (Annual Dividends / Current Price) × 100
- **Thresholds**:
  - Bad: < 1%
  - Normal: 1% - 4%
  - Excellent: > 4%
- **Note**: Adapt cut-offs for REITs/MLPs if needed

#### Average Yield
- **Calculation**: Mean of historical yields in analysis window
- **Thresholds**: Same as Current Yield

#### Maximum Yield
- **Calculation**: Maximum historical yield in analysis window
- **Thresholds**:
  - Bad: < 2%
  - Normal: 2% - 6%
  - Excellent: > 6%
- **Note**: Helps flag "special" payouts

### Important Caveats

1. **Dividend Yields**: High (> 8%) yields can signal distress. Consider adding a "Too High" red band above ~8%.

2. **Market Context**: These thresholds are designed for developed-market equities. Adjust for:
   - Fixed income securities
   - Emerging markets
   - Cryptocurrencies
   - Alternative assets

3. **Time Period**: Analysis windows provide more reliable metrics, especially for:
   - Volatility
   - Maximum drawdown
   - Beta calculations

4. **Benchmark Selection**: The SPY benchmark is used by default, but consider using:
   - Sector-specific ETFs for sector analysis
   - Regional indices for geographic analysis
   - Custom benchmarks for specific mandates

---

## 3. Documentation & Version Management Updates (v4.5.1)

### Overview
This release focuses on comprehensive documentation updates, version management improvements, and system maintenance to ensure all documentation reflects the current state of the application.

### Documentation System Enhancements

#### Comprehensive Documentation Updates
- **AI.MD Updates**: Updated technical overview to reflect v4.5.1 architecture and current system capabilities
- **ARCHITECTURE.md Refinement**: Enhanced architecture documentation with current system features and design patterns
- **BACKEND.MD Enhancement**: Updated backend documentation with current API endpoints and service architecture
- **FRONTEND.MD Updates**: Enhanced frontend documentation with current component structure and features
- **METRICS.MD Clarification**: Improved metric explanations and threshold descriptions for different investment mandates
- **STYLE.MD Simplification**: Updated design system documentation with simplified language and improved clarity
- **structure.md Enhancement**: Updated repository structure documentation with current features and capabilities

#### Version Management Improvements
- **Automated Version Updates**: Enhanced version update script with better file detection and error handling
- **Cross-Platform Compatibility**: Improved version update script compatibility across different operating systems
- **Version Synchronization**: Ensured all version references are consistent across frontend, backend, and documentation
- **File Validation**: Enhanced file validation and error reporting in version management tools

### Technical Implementation

#### Documentation Architecture
- **Centralized Version Management**: All documentation now references v4.5.1 consistently
- **Modular Documentation**: Each documentation file focuses on specific aspects of the system
- **Cross-Reference Updates**: All internal links and references updated to current structure
- **Version History**: Maintained comprehensive changelog with detailed version information

#### Version Management System
- **Automated Updates**: Enhanced version update script with better file detection
- **Error Recovery**: Improved error handling and recovery mechanisms
- **Platform Compatibility**: Better cross-platform support for version updates
- **File Validation**: Enhanced file validation and error reporting

### Metrics System Benefits

#### Developer Experience
- **Consistent Documentation**: All documentation now reflects current system state
- **Better Maintenance**: Easier to maintain and update documentation
- **Version Clarity**: Clear version management and update process
- **Code Quality**: Improved code organization and maintainability

#### System Reliability
- **Documentation Accuracy**: Ensures documentation matches actual system capabilities
- **Version Consistency**: Prevents version-related confusion and errors
- **Maintainability**: Easier to maintain and extend the system
- **Quality Assurance**: Better documentation quality and consistency

### Evidence
- `scripts/update_version.py` - Enhanced version update script
- `CHANGELOG.md` - Comprehensive version history and changes
- `docs/` - Updated documentation files across all components 