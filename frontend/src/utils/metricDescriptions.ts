/**
 * Metric descriptions and tooltips for ticker analysis
 */

export interface MetricDescription {
  name: string;
  description: string;
  formula: string;
  thresholds: string;
}

export const TICKER_METRIC_DESCRIPTIONS: Record<string, MetricDescription> = {
  totalReturn: {
    name: 'Total Return',
    description: 'Overall ticker return for the analysis period',
    formula: '(End Price / Start Price) - 1',
    thresholds: 'Red <5%, Yellow 5-20%, Green >20%'
  },
  annualizedReturn: {
    name: 'Annualized Return',
    description: 'Return adjusted for time period',
    formula: '(1 + Total Return)^(252/days) - 1',
    thresholds: 'Red <5%, Yellow 5-20%, Green >20%'
  },
  volatility: {
    name: 'Volatility',
    description: 'Standard deviation of daily returns',
    formula: 'std_daily_return × √252',
    thresholds: 'Red >50%, Yellow 30-50%, Green <30%'
  },
  sharpeRatio: {
    name: 'Sharpe Ratio',
    description: 'Risk-adjusted return measure',
    formula: '√252 × (mean - rf) / std',
    thresholds: 'Red <0.5, Yellow 0.5-1.5, Green >1.5'
  },
  maxDrawdown: {
    name: 'Max Drawdown',
    description: 'Maximum peak-to-trough decline',
    formula: 'min((current - max) / max)',
    thresholds: 'Red >-50%, Yellow -50% to -30%, Green >-30%'
  },
  annualizedDividend: {
    name: 'Annualized Dividend',
    description: 'Annualized dividend amount per share',
    formula: 'Dividend Amount × Frequency',
    thresholds: 'Red <$1, Yellow $1-$4, Green >$4'
  },
  dividendYield: {
    name: 'Dividend Yield',
    description: 'Annualized dividend yield percentage',
    formula: 'Annualized Dividend / Current Price',
    thresholds: 'Red <1%, Yellow 1-4%, Green >4%'
  },
  momentum12to1: {
    name: 'Momentum (12-1)',
    description: 'Price momentum over 12 months (excluding last month)',
    formula: '(Price 12m ago - Price 1m ago) / Price 12m ago',
    thresholds: 'Red <0%, Yellow 0-20%, Green >20%'
  },
  beta: {
    name: 'Beta',
    description: 'Market sensitivity vs S&P 500',
    formula: 'cov(ticker, benchmark) / var(benchmark)',
    thresholds: 'Red >1.5, Yellow 0.5-1.5, Green <0.5'
  },
  var95: {
    name: 'VaR (95%)',
    description: 'Value at Risk - max expected loss',
    formula: '-(1.645 × std - mean) × 100',
    thresholds: 'Red >-4%, Yellow -4% to -2%, Green >-2%'
  },
  sortinoRatio: {
    name: 'Sortino Ratio',
    description: 'Downside risk-adjusted return',
    formula: '√252 × (mean - rf) / std_downside',
    thresholds: 'Red <0.8, Yellow 0.8-2.0, Green >2.0'
  }
};

export function getMetricDescription(metricName: string): MetricDescription | null {
  return TICKER_METRIC_DESCRIPTIONS[metricName] || null;
}
