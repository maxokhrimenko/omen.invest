/**
 * Shared timeout calculation utilities for portfolio analysis.
 * 
 * This module provides consistent timeout calculation across backend and frontend
 * based on portfolio size and date range.
 */

export interface TimeoutBreakdown {
  tickerCount: number;
  dateRangeDays: number;
  dateRangeYears: number;
  baseTimeout: number;
  secondsPerTickerPerYear: number;
  dynamicComponent: number;
  calculatedTimeout: number;
  finalTimeout: number;
}

/**
 * Calculate dynamic timeout for portfolio analysis based on ticker count and date range.
 * 
 * @param tickerCount Number of tickers in the portfolio
 * @param startDate Analysis start date (YYYY-MM-DD format)
 * @param endDate Analysis end date (YYYY-MM-DD format)
 * @param baseTimeout Base timeout in seconds (default: 30)
 * @param secondsPerTickerPerYear Seconds per ticker per year of data (default: 0.2)
 * @returns Calculated timeout in seconds
 */
export function calculateAnalysisTimeout(
  tickerCount: number,
  startDate: string,
  endDate: string,
  baseTimeout: number = 30,
  secondsPerTickerPerYear: number = 0.2
): number {
  try {
    // Parse dates
    const startDt = new Date(startDate);
    const endDt = new Date(endDate);
    
    // Calculate date range in years
    const dateRangeDays = Math.ceil((endDt.getTime() - startDt.getTime()) / (1000 * 60 * 60 * 24));
    const dateRangeYears = Math.max(1, dateRangeDays / 365.25); // Minimum 1 year
    
    // Calculate dynamic timeout
    // Formula: base_timeout + (ticker_count * date_range_years * seconds_per_ticker_per_year)
    const dynamicTimeout = baseTimeout + (tickerCount * dateRangeYears * secondsPerTickerPerYear);
    
    // Apply reasonable bounds
    const minTimeout = 30; // Minimum 30 seconds
    const maxTimeout = 600; // Maximum 10 minutes
    
    const calculatedTimeout = Math.max(minTimeout, Math.min(dynamicTimeout, maxTimeout));
    
    return Math.floor(calculatedTimeout);
    
  } catch (error) {
    // If date parsing fails, return base timeout
    console.warn('Failed to parse dates for timeout calculation:', error);
    return baseTimeout;
  }
}

/**
 * Get detailed breakdown of timeout calculation for debugging.
 * 
 * @param tickerCount Number of tickers in the portfolio
 * @param startDate Analysis start date (YYYY-MM-DD format)
 * @param endDate Analysis end date (YYYY-MM-DD format)
 * @returns Object with timeout calculation details
 */
export function getTimeoutBreakdown(
  tickerCount: number,
  startDate: string,
  endDate: string
): TimeoutBreakdown | { error: string; fallbackTimeout: number } {
  try {
    const startDt = new Date(startDate);
    const endDt = new Date(endDate);
    
    const dateRangeDays = Math.ceil((endDt.getTime() - startDt.getTime()) / (1000 * 60 * 60 * 24));
    const dateRangeYears = Math.max(1, dateRangeDays / 365.25);
    
    const baseTimeout = 30;
    const secondsPerTickerPerYear = 0.2;
    
    const dynamicComponent = tickerCount * dateRangeYears * secondsPerTickerPerYear;
    const calculatedTimeout = baseTimeout + dynamicComponent;
    const finalTimeout = calculateAnalysisTimeout(tickerCount, startDate, endDate);
    
    return {
      tickerCount,
      dateRangeDays,
      dateRangeYears: Math.round(dateRangeYears * 100) / 100,
      baseTimeout,
      secondsPerTickerPerYear,
      dynamicComponent: Math.round(dynamicComponent * 100) / 100,
      calculatedTimeout: Math.floor(calculatedTimeout),
      finalTimeout
    };
  } catch (error) {
    return {
      error: 'Invalid date format',
      fallbackTimeout: 30
    };
  }
}

/**
 * Format timeout duration for display
 * 
 * @param timeoutSeconds Timeout in seconds
 * @returns Formatted timeout string
 */
export function formatTimeout(timeoutSeconds: number): string {
  if (timeoutSeconds < 60) {
    return `${timeoutSeconds}s`;
  } else if (timeoutSeconds < 3600) {
    const minutes = Math.floor(timeoutSeconds / 60);
    const seconds = timeoutSeconds % 60;
    return seconds > 0 ? `${minutes}m ${seconds}s` : `${minutes}m`;
  } else {
    const hours = Math.floor(timeoutSeconds / 3600);
    const minutes = Math.floor((timeoutSeconds % 3600) / 60);
    return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
  }
}

// Example usage and testing
if (typeof window !== 'undefined') {
  // Browser environment - add to window for debugging
  (window as any).timeoutCalculator = {
    calculateAnalysisTimeout,
    getTimeoutBreakdown,
    formatTimeout
  };
}
