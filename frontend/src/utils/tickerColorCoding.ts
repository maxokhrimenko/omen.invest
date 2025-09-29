/**
 * Financial metrics color coding utility based on METRICS.md and STYLE.MD thresholds
 * Supports both portfolio-level and ticker-level metrics with appropriate thresholds
 */

export type MetricLevel = 'excellent' | 'normal' | 'poor';

export interface ColorThresholds {
  poor: number;
  excellent: number;
}

export interface MetricThresholds {
  [key: string]: ColorThresholds;
}

// Portfolio-level thresholds (for consolidated portfolio analysis)
export const PORTFOLIO_THRESHOLDS: MetricThresholds = {
  // Return Metrics
  totalReturn: { poor: 10.0, excellent: 30.0 }, // Red <10%, Yellow 10-30%, Green >30%
  annualizedReturn: { poor: 5.0, excellent: 15.0 }, // Red <5%, Yellow 5-15%, Green >15%
  
  // Risk-Adjusted Return Metrics
  sharpeRatio: { poor: 0.5, excellent: 1.5 }, // Red <0.5, Yellow 0.5-1.5, Green >1.5
  sortinoRatio: { poor: 1.0, excellent: 2.0 }, // Red <1.0, Yellow 1.0-2.0, Green >2.0
  calmarRatio: { poor: 0.5, excellent: 1.5 }, // Red <0.5, Yellow 0.5-1.5, Green >1.5
  
  // Risk Metrics
  maxDrawdown: { poor: -50.0, excellent: -20.0 }, // Red <-50%, Yellow -50% to -20%, Green >-20%
  volatility: { poor: 20.0, excellent: 10.0 }, // Red >20%, Yellow 10-20%, Green <10%
  var95: { poor: -5.0, excellent: -2.0 }, // Red <-5%, Yellow -5% to -2%, Green >-2%
  cvar95: { poor: -5.0, excellent: -2.0 }, // Same as var95
  beta: { poor: 1.3, excellent: 0.7 }, // Red >1.3, Yellow 0.7-1.3, Green <0.7
  
  // Advanced Risk Metrics
  ulcerIndex: { poor: 15.0, excellent: 5.0 }, // Red >15, Yellow 5-15, Green <5
  timeUnderWater: { poor: 50.0, excellent: 20.0 }, // Red >50%, Yellow 20-50%, Green <20%
};

// Ticker-level thresholds (for individual securities)
export const TICKER_THRESHOLDS: MetricThresholds = {
  // Return Metrics
  annualizedReturn: { poor: 5.0, excellent: 20.0 }, // Red <5%, Yellow 5-20%, Green >20%
  totalReturn: { poor: 5.0, excellent: 20.0 }, // Same as annualized for tickers
  
  // Risk-Adjusted Return Metrics
  sharpeRatio: { poor: 0.5, excellent: 1.5 }, // Red <0.5, Yellow 0.5-1.5, Green >1.5
  sortinoRatio: { poor: 0.8, excellent: 2.0 }, // Red <0.8, Yellow 0.8-2.0, Green >2.0
  calmarRatio: { poor: 0.5, excellent: 1.5 }, // Red <0.5, Yellow 0.5-1.5, Green >1.5
  
  // Risk Metrics
  maxDrawdown: { poor: -50.0, excellent: -30.0 }, // Red <-50%, Yellow -50% to -30%, Green >-30%
  volatility: { poor: 50.0, excellent: 30.0 }, // Red >50%, Yellow 30-50%, Green <30%
  beta: { poor: 1.5, excellent: 0.5 }, // Red >1.5, Yellow 0.5-1.5, Green <0.5
  var95: { poor: -4.0, excellent: -2.0 }, // Red <-4%, Yellow -4% to -2%, Green >-2%
  cvar95: { poor: -4.0, excellent: -2.0 }, // Same as var95
  
  // Advanced Risk Metrics
  ulcerIndex: { poor: 15.0, excellent: 5.0 }, // Red >15, Yellow 5-15, Green <5
  timeUnderWater: { poor: 30.0, excellent: 10.0 }, // Red >30%, Yellow 10-30%, Green <10%
  correlationToPortfolio: { poor: 0.75, excellent: 0.25 }, // Red >0.75, Yellow 0.25-0.75, Green <0.25
  riskContributionPercent: { poor: 40.0, excellent: 10.0 }, // Red >40%, Yellow 10-40%, Green <10%
  
  // Momentum and Yield Metrics
  momentum12to1: { poor: 0.0, excellent: 20.0 }, // Red <0%, Yellow 0-20%, Green >20%
  dividendYield: { poor: 1.0, excellent: 4.0 }, // Red <1%, Yellow 1-4%, Green >4%
  annualizedDividend: { poor: 1.0, excellent: 4.0 }, // Same as dividend yield
  maximumYield: { poor: 2.0, excellent: 6.0 }, // Red <2%, Yellow 2-6%, Green >6%
};

export function getMetricLevel(metricName: string, value: number, isPortfolio: boolean = false): MetricLevel {
  const thresholds = isPortfolio ? PORTFOLIO_THRESHOLDS[metricName] : TICKER_THRESHOLDS[metricName];
  if (!thresholds) return 'normal';
  
  const { poor, excellent } = thresholds;
  
  // Handle special cases for metrics where lower is better
  if (metricName === 'volatility') {
    if (value > poor) return 'poor';
    if (value < excellent) return 'excellent';
    return 'normal';
  }
  
  // Handle var95 and cvar95 separately - less negative is better
  if (metricName === 'var95' || metricName === 'cvar95') {
    if (value < poor) return 'poor'; // More negative than threshold (e.g., -5% vs -4%)
    if (value < excellent) return 'normal'; // Between thresholds (e.g., -3% vs -2%)
    return 'excellent'; // Less negative than excellent threshold (e.g., -1%)
  }
  
  // Handle maxDrawdown separately - less negative is better
  if (metricName === 'maxDrawdown') {
    if (value < poor) return 'poor'; // More negative than poor threshold
    if (value < excellent) return 'normal'; // Between poor and excellent thresholds
    return 'excellent'; // Less negative than excellent threshold
  }
  
  // Handle beta separately - closer to 1.0 is better
  if (metricName === 'beta') {
    const distanceFromOne = Math.abs(value - 1.0);
    const poorThreshold = Math.abs(poor - 1.0); // Distance from 1.0 for poor threshold
    const excellentThreshold = Math.abs(excellent - 1.0); // Distance from 1.0 for excellent threshold
    
    if (distanceFromOne > poorThreshold) return 'poor';
    if (distanceFromOne < excellentThreshold) return 'excellent';
    return 'normal';
  }
  
  // Handle advanced risk metrics where lower is better
  if (metricName === 'ulcerIndex' || metricName === 'timeUnderWater' || metricName === 'correlationToPortfolio' || metricName === 'riskContributionPercent') {
    if (value > poor) return 'poor';
    if (value < excellent) return 'excellent';
    return 'normal';
  }
  
  // Standard case where higher is better
  if (value < poor) return 'poor';
  if (value > excellent) return 'excellent';
  return 'normal';
}

export function getMetricColorClasses(metricName: string, value: number, isPortfolio: boolean = false): string {
  const level = getMetricLevel(metricName, value, isPortfolio);
  
  switch (level) {
    case 'excellent':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'normal':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'poor':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}

export function getMetricTextColor(metricName: string, value: number, isPortfolio: boolean = false): string {
  const level = getMetricLevel(metricName, value, isPortfolio);
  
  switch (level) {
    case 'excellent':
      return 'text-green-600';
    case 'normal':
      return 'text-yellow-600';
    case 'poor':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
}

// Convenience functions for portfolio-specific color coding
export function getPortfolioMetricColorClasses(metricName: string, value: number): string {
  return getMetricColorClasses(metricName, value, true);
}

export function getPortfolioMetricTextColor(metricName: string, value: number): string {
  return getMetricTextColor(metricName, value, true);
}

export function parseMetricValue(value: string | undefined): number | null {
  if (!value || value === 'N/A') return null;
  
  // Remove common prefixes and suffixes
  const cleanValue = value.replace(/[%,$]/g, '');
  const numValue = parseFloat(cleanValue);
  
  return isNaN(numValue) ? null : numValue;
}

export function getThresholdDescription(metricName: string, isPortfolio: boolean = false): string {
  const thresholds = isPortfolio ? PORTFOLIO_THRESHOLDS[metricName] : TICKER_THRESHOLDS[metricName];
  if (!thresholds) return '';
  
  const { poor, excellent } = thresholds;
  
  // Handle special cases for metrics where lower is better
  if (metricName === 'maxDrawdown' || metricName === 'volatility' || metricName === 'beta' || metricName === 'var95' || metricName === 'cvar95') {
    return `Red >${poor}%, Yellow ${excellent}% to ${poor}%, Green <${excellent}%`;
  }
  
  // Handle advanced risk metrics where lower is better
  if (metricName === 'ulcerIndex' || metricName === 'timeUnderWater' || metricName === 'correlationToPortfolio' || metricName === 'riskContributionPercent') {
    return `Red >${poor}%, Yellow ${excellent}% to ${poor}%, Green <${excellent}%`;
  }
  
  // Standard case where higher is better
  return `Red <${poor}%, Yellow ${poor}% to ${excellent}%, Green >${excellent}%`;
}

// Convenience function for portfolio-specific threshold descriptions
export function getPortfolioThresholdDescription(metricName: string): string {
  return getThresholdDescription(metricName, true);
}
