# 📊 Investment Metrics Memorandum

This document explains all metrics used in the portfolio analysis tool, their calculations, and thresholds.

*This metrics documentation reflects version 4.5.3 of the Portfolio Analysis Tool with advanced risk metrics, enhanced ticker comparison, and comprehensive portfolio analysis capabilities.*

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
- **Calculation**: (mean(r_t) × A - MAR_annual) / (sqrt(DownDev²) × sqrt(A))
- **Thresholds**:
  - Bad: < 1
  - Normal: 1 - 2
  - Excellent: > 2
- **Note**: Uses downside deviation; MAR = 0 unless specified

#### Calmar Ratio
- **Calculation**: Calmar = CAGR / |MDD|, where CAGR = W_T^(A/N) - 1
- **Thresholds**:
  - Bad: < 0.5
  - Normal: 0.5 - 1.5
  - Excellent: > 1.5
- **Note**: Sensitive to the horizon length; often used for funds

### Risk Metrics

#### Max Drawdown
- **Calculation**: DD_t = W_t / max_{s≤t} W_s - 1; MDD = min_t DD_t
- **Thresholds**:
  - Bad: < -50%
  - Normal: -20% to -50%
  - Excellent: > -20%
- **Note**: Use portfolio-level W_{p,t} when assessing overall strategy risk

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

#### Ulcer Index
- **Calculation**: UI = sqrt((1/N) × Σ [max(0, 1 - W_t / max_{s≤t} W_s)]²)
- **Thresholds**:
  - Bad: > 15
  - Normal: 5 - 15
  - Excellent: < 5
- **Note**: Measures depth and duration of drawdowns

#### Time Under Water
- **Calculation**: TUW = (1/N) × Σ 1{W_t < max_{s≤t} W_s}
- **Thresholds**:
  - Bad: > 50%
  - Normal: 20% - 50%
  - Excellent: < 20%
- **Note**: Indicates persistence of losses relative to peaks

#### Historical Expected Shortfall (CVaR_95)
- **Calculation**: CVaR_95 = (1/k) × Σ_{j=1..k} r_{(j)}, with k = floor(0.05 × N)
- **Thresholds**:
  - Bad: < -5% daily
  - Normal: -2% to -5% daily
  - Excellent: > -2% daily
- **Note**: Reports tail loss; for h-day scaling, CVaR_h ≈ sqrt(h) × CVaR_1

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

#### Correlation to Portfolio (Diversifier Score)
- **Calculation**: ρ_{i,p} = cov(r_i, r_p) / (σ_i × σ_p)
- **Thresholds**:
  - Bad: > 0.75
  - Normal: 0.25 - 0.75
  - Excellent: < 0.25
- **Note**: Lower correlation implies better diversification benefit

#### Risk Contribution to Portfolio Variance
- **Calculation**: 
  - Absolute: AC_i = w_i × m_i, where m = Σ w
  - Percent: PC_i = AC_i / σ_p²
- **Thresholds**:
  - Bad: Concentration > 40% in a single asset
  - Normal: 10% - 40% per asset
  - Excellent: < 10% per asset
- **Note**: If using stdev, RC_i = (w_i × m_i) / σ_p with Σ RC_i = σ_p

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

### Advanced Risk Metrics (v4.5.3)

#### Calmar Ratio
- **Calculation**: Annualized Return / |Maximum Drawdown|
- **Thresholds**:
  - Bad: < 0.5
  - Normal: 0.5 - 1.0
  - Excellent: > 1.0
- **Note**: Risk-adjusted return metric focusing on drawdown-adjusted performance

#### Ulcer Index
- **Calculation**: √(Σ(DD²) / N) where DD = (High - Close) / High
- **Thresholds**:
  - Bad: > 0.05
  - Normal: 0.02 - 0.05
  - Excellent: < 0.02
- **Note**: Downside risk measure focusing on depth and duration of drawdowns

#### Time Under Water
- **Calculation**: (Days in Drawdown / Total Days) × 100
- **Thresholds**:
  - Bad: > 40%
  - Normal: 20% - 40%
  - Excellent: < 20%
- **Note**: Percentage of time spent in drawdown periods

#### CVaR (Conditional Value at Risk)
- **Calculation**: Expected loss beyond VaR threshold at 95% confidence level
- **Thresholds**:
  - Bad: < -4%
  - Normal: -4% to -2%
  - Excellent: > -2%
- **Note**: Expected loss beyond VaR threshold, more conservative than VaR

#### Portfolio Correlation
- **Calculation**: Correlation coefficient between individual ticker and portfolio returns
- **Thresholds**:
  - Bad: > 0.8
  - Normal: 0.4 - 0.8
  - Excellent: < 0.4
- **Note**: Lower correlation indicates better diversification potential

#### Risk Contribution (Absolute)
- **Calculation**: Ticker's contribution to portfolio variance
- **Thresholds**:
  - Bad: > 0.01
  - Normal: 0.005 - 0.01
  - Excellent: < 0.005
- **Note**: Absolute risk contribution to portfolio risk

#### Risk Contribution (Percentage)
- **Calculation**: (Ticker's Risk Contribution / Total Portfolio Risk) × 100
- **Thresholds**:
  - Bad: > 20%
  - Normal: 10% - 20%
  - Excellent: < 10%
- **Note**: Percentage of portfolio risk contributed by this ticker

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

## 3. Documentation & Version Management Updates (v4.6.0)

### Overview
This release focuses on enhanced risk metrics, improved calculations, and comprehensive portfolio analysis capabilities with advanced risk measurement tools.

### Documentation System Enhancements

#### Enhanced Risk Metrics Documentation
- **Advanced Risk Metrics**: Added comprehensive documentation for Ulcer Index, Time Under Water, and Historical Expected Shortfall
- **Improved Calculations**: Updated Max Drawdown, Calmar Ratio, and Sortino Ratio with more precise mathematical formulations
- **Diversification Metrics**: Added Correlation to Portfolio and Risk Contribution to Portfolio Variance metrics
- **Threshold Refinements**: Updated thresholds based on industry best practices and risk management standards
- **Mathematical Precision**: Enhanced calculation formulas with proper mathematical notation and scaling factors

#### Risk Management Enhancements
- **Advanced Risk Assessment**: Comprehensive suite of risk metrics for portfolio and individual asset analysis
- **Mathematical Rigor**: Precise calculations with proper scaling and statistical foundations
- **Industry Standards**: Thresholds aligned with institutional risk management practices
- **Diversification Analysis**: Enhanced tools for assessing portfolio diversification and concentration risk

### Technical Implementation

#### Risk Metrics Architecture
- **Comprehensive Coverage**: Complete suite of risk metrics covering return, volatility, drawdown, and diversification
- **Mathematical Foundation**: Rigorous mathematical formulations with proper statistical foundations
- **Scalable Framework**: Metrics designed to work across different asset classes and time horizons
- **Industry Alignment**: Thresholds and calculations aligned with institutional risk management standards

#### Advanced Risk Calculations
- **Drawdown Analysis**: Enhanced Max Drawdown with proper mathematical formulation and portfolio-level assessment
- **Risk-Adjusted Returns**: Improved Sortino and Calmar ratios with precise calculations and scaling
- **Tail Risk Metrics**: Historical Expected Shortfall for comprehensive tail risk assessment
- **Diversification Tools**: Correlation and risk contribution metrics for portfolio optimization

### Enhanced Risk Analysis Benefits

#### Portfolio Management
- **Comprehensive Risk Assessment**: Complete suite of risk metrics for thorough portfolio analysis
- **Advanced Drawdown Analysis**: Enhanced understanding of portfolio drawdown patterns and recovery
- **Diversification Optimization**: Tools for assessing and improving portfolio diversification
- **Tail Risk Management**: Better understanding and management of extreme loss scenarios

#### Risk Management
- **Institutional Standards**: Metrics aligned with professional risk management practices
- **Mathematical Rigor**: Precise calculations with proper statistical foundations
- **Multi-Asset Support**: Metrics designed to work across different asset classes
- **Scalable Framework**: Risk analysis that scales from individual assets to entire portfolios

### Evidence
- `docs/METRICS.md` - Enhanced risk metrics documentation with advanced calculations
- `backend/src/infrastructure/services/metrics_calculator.py` - Implementation of advanced risk metrics
- `frontend/src/components/portfolio/AdvancedMetricsCards.tsx` - UI components for new metrics
- `CHANGELOG.md` - Comprehensive version history and risk metric enhancements 