/**
 * Ticker metrics color coding utility based on CLI thresholds from METRICS_MEMORANDUM.md
 */

export type MetricLevel = 'excellent' | 'normal' | 'poor';

export interface ColorThresholds {
  poor: number;
  excellent: number;
}

export interface MetricThresholds {
  [key: string]: ColorThresholds;
}

// Ticker metric thresholds from CLI ColorMetricsService
export const TICKER_THRESHOLDS: MetricThresholds = {
  // Return Metrics
  annualizedReturn: { poor: 5.0, excellent: 20.0 }, // Red <5%, Yellow 5-20%, Green >20%
  totalReturn: { poor: 5.0, excellent: 20.0 }, // Same as annualized for tickers
  
  // Risk-Adjusted Return Metrics
  sharpeRatio: { poor: 0.5, excellent: 1.5 }, // Red <0.5, Yellow 0.5-1.5, Green >1.5
  sortinoRatio: { poor: 0.8, excellent: 2.0 }, // Red <0.8, Yellow 0.8-2.0, Green >2.0
  
  // Risk Metrics
  maxDrawdown: { poor: -50.0, excellent: -30.0 }, // Red >-50%, Yellow -50% to -30%, Green >-30%
  volatility: { poor: 50.0, excellent: 30.0 }, // Red >50%, Yellow 30-50%, Green <30%
  beta: { poor: 1.5, excellent: 0.5 }, // Red >1.5, Yellow 0.5-1.5, Green <0.5
  var95: { poor: -4.0, excellent: -2.0 }, // Red >-4%, Yellow -4% to -2%, Green >-2%
  
  // Momentum and Yield Metrics
  momentum12to1: { poor: 0.0, excellent: 20.0 }, // Red <0%, Yellow 0-20%, Green >20%
  dividendYield: { poor: 1.0, excellent: 4.0 }, // Red <1%, Yellow 1-4%, Green >4%
  annualizedDividend: { poor: 1.0, excellent: 4.0 }, // Same as dividend yield
};

export function getMetricLevel(metricName: string, value: number): MetricLevel {
  const thresholds = TICKER_THRESHOLDS[metricName];
  if (!thresholds) return 'normal';
  
  const { poor, excellent } = thresholds;
  
  // Handle special cases for metrics where lower is better
  if (metricName === 'volatility') {
    if (value > poor) return 'poor';
    if (value < excellent) return 'excellent';
    return 'normal';
  }
  
  // Handle var95 separately - less negative is better
  if (metricName === 'var95') {
    if (value < poor) return 'poor'; // More negative than -4% (e.g., -5%)
    if (value < excellent) return 'normal'; // Between -4% and -2% (e.g., -3%)
    return 'excellent'; // Less negative than -2% (e.g., -1%)
  }
  
  // Handle maxDrawdown separately - less negative is better
  if (metricName === 'maxDrawdown') {
    if (value < poor) return 'poor'; // More negative than -50% (e.g., -60%)
    if (value < excellent) return 'normal'; // Between -50% and -30% (e.g., -40%)
    return 'excellent'; // Less negative than -30% (e.g., -7%)
  }
  
  // Handle beta separately - closer to 1.0 is better
  if (metricName === 'beta') {
    const distanceFromOne = Math.abs(value - 1.0);
    if (distanceFromOne > 0.5) return 'poor'; // >1.5 or <0.5
    if (distanceFromOne > 0.3) return 'normal'; // 0.7-1.3
    return 'excellent'; // 0.7-1.3
  }
  
  // Standard case where higher is better
  if (value < poor) return 'poor';
  if (value > excellent) return 'excellent';
  return 'normal';
}

export function getMetricColorClasses(metricName: string, value: number): string {
  const level = getMetricLevel(metricName, value);
  
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

export function getMetricTextColor(metricName: string, value: number): string {
  const level = getMetricLevel(metricName, value);
  
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

export function parseMetricValue(value: string | undefined): number | null {
  if (!value || value === 'N/A') return null;
  
  // Remove common prefixes and suffixes
  const cleanValue = value.replace(/[%,$]/g, '');
  const numValue = parseFloat(cleanValue);
  
  return isNaN(numValue) ? null : numValue;
}

export function getThresholdDescription(metricName: string): string {
  const thresholds = TICKER_THRESHOLDS[metricName];
  if (!thresholds) return '';
  
  const { poor, excellent } = thresholds;
  
  // Handle special cases for metrics where lower is better
  if (metricName === 'maxDrawdown' || metricName === 'volatility' || metricName === 'beta' || metricName === 'var95') {
    return `Red >${poor}%, Yellow ${excellent}% to ${poor}%, Green <${excellent}%`;
  }
  
  // Standard case where higher is better
  return `Red <${poor}%, Yellow ${poor}% to ${excellent}%, Green >${excellent}%`;
}
