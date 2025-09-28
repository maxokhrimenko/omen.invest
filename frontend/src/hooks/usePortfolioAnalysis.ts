import { useState, useCallback, useEffect } from 'react';
import type { DateRange } from '../components/portfolio/DateRangeSelector';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import { useToast } from './useToast';
import { calculateAnalysisTimeout, formatTimeout } from '../utils/timeoutCalculator';

export interface PortfolioMetrics {
  totalReturn: string;
  annualizedReturn: string;
  volatility: string;
  sharpeRatio: string;
  maxDrawdown: string;
  sortinoRatio: string;
  calmarRatio: string;
  var95: string;
  beta: string;
  startValue: string;
  endValue: string;
  endValueAnalysis: string;
  endValueMissing: string;
  dividendAmount: string;
  annualizedDividendYield: string;
  totalDividendYield: string;
}

// TickerMetrics removed - ticker analysis will be separate feature

export interface DataWarnings {
  missingTickers: string[];
  tickersWithoutStartData: string[];
  firstAvailableDates: { [ticker: string]: string };
}

export interface AnalysisResults {
  portfolioMetrics: PortfolioMetrics;
  dataWarnings: DataWarnings;
  analysisDate: string;
  dateRange: DateRange;
  timeSeriesData: {
    portfolioValues: Record<string, number>;
    sp500Values: Record<string, number>;
    nasdaqValues: Record<string, number>;
  };
}

export const usePortfolioAnalysis = () => {
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange | null>(null);
  const { showToast, hideToast } = useToast();

  // Load analysis results from localStorage on mount
  useEffect(() => {
    const savedResults = localStorage.getItem('portfolioAnalysisResults');
    const savedDateRange = localStorage.getItem('portfolioAnalysisDateRange');
    
    if (savedResults) {
      try {
        setAnalysisResults(JSON.parse(savedResults));
      } catch {
        // Clear invalid saved data
        localStorage.removeItem('portfolioAnalysisResults');
      }
    }
    
    if (savedDateRange) {
      try {
        setSelectedDateRange(JSON.parse(savedDateRange));
      } catch {
        // Clear invalid saved data
        localStorage.removeItem('portfolioAnalysisDateRange');
      }
    }
  }, []);

  // Save analysis results to localStorage
  const saveAnalysisResults = useCallback((results: AnalysisResults) => {
    localStorage.setItem('portfolioAnalysisResults', JSON.stringify(results));
  }, []);

  // Clear analysis results
  const clearAnalysis = useCallback(() => {
    setAnalysisResults(null);
    setError(null);
    localStorage.removeItem('portfolioAnalysisResults');
    localStorage.removeItem('portfolioAnalysisDateRange');
  }, []);

  // Clear cache and reload data (no-op since we don't use cache)
  const clearCacheAndReload = useCallback(() => {
    setAnalysisResults(null);
    setError(null);
  }, []);

  // Run portfolio analysis
  const runAnalysis = useCallback(async (startDate: string, endDate: string, tickerCount?: number) => {
    setIsLoading(true);
    setError(null);

    // Calculate estimated timeout for toast message
    const estimatedTimeout = tickerCount 
      ? calculateAnalysisTimeout(tickerCount, startDate, endDate)
      : null;
    
    const estimatedTimeText = estimatedTimeout 
      ? ` (Estimated: ${formatTimeout(estimatedTimeout)})`
      : '';

    // Show loading toast
    const loadingToastId = showToast({
      type: 'loading',
      title: 'Analysis in Progress',
      message: `Analyzing portfolio${estimatedTimeText}...`,
      persistent: true
    });

    try {
      logger.info('Starting portfolio analysis', { 
        operation: 'portfolio_analysis',
        startDate, 
        endDate, 
        tickerCount 
      });
      
      // Call only portfolio analysis API endpoint (matching CLI behavior)
      const portfolioResponse = await apiService.analyzePortfolio(startDate, endDate, tickerCount);

      logger.info('API response received', { 
        operation: 'api_responses',
        portfolioSuccess: portfolioResponse.success, 
        portfolioData: portfolioResponse.data
      });

      if (!portfolioResponse.success) {
        throw new Error(portfolioResponse.message);
      }

      // Convert API response to our internal format (portfolio metrics only)
      const analysisResults: AnalysisResults = {
        portfolioMetrics: portfolioResponse.data,
        dataWarnings: {
          missingTickers: portfolioResponse.warnings.missingTickers,
          tickersWithoutStartData: portfolioResponse.warnings.tickersWithoutStartData,
          firstAvailableDates: portfolioResponse.warnings.firstAvailableDates || {}
        },
        analysisDate: new Date().toISOString(),
        dateRange: selectedDateRange || {
          startDate,
          endDate,
          label: 'Custom Range',
          type: 'custom'
        },
        timeSeriesData: portfolioResponse.timeSeriesData || {
          portfolioValues: {},
          sp500Values: {},
          nasdaqValues: {}
        }
      };

      logger.info('Analysis results created successfully', {
        operation: 'analysis_complete',
        hasPortfolioMetrics: !!analysisResults.portfolioMetrics
      });
      setAnalysisResults(analysisResults);
      saveAnalysisResults(analysisResults);
      
      // Save date range to localStorage
      const dateRange = selectedDateRange || {
        startDate,
        endDate,
        label: 'Custom Range',
        type: 'custom'
      };
      setSelectedDateRange(dateRange);
      localStorage.setItem('portfolioAnalysisDateRange', JSON.stringify(dateRange));
      
      // Hide loading toast and show success toast
      hideToast(loadingToastId);
      showToast({
        type: 'success',
        title: 'Analysis Complete',
        message: `Portfolio analysis completed successfully${estimatedTimeText}`,
        duration: 3000
      });
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      logger.error('Portfolio analysis failed', err as Error, {
        operation: 'portfolio_analysis',
        startDate,
        endDate,
        tickerCount,
        message: errorMessage
      });
      setError(errorMessage);
      
      // Hide loading toast and show error toast
      hideToast(loadingToastId);
      showToast({
        type: 'error',
        title: 'Analysis Failed',
        message: errorMessage,
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  }, [selectedDateRange, saveAnalysisResults, showToast, hideToast]);

  return {
    analysisResults,
    isLoading,
    error,
    selectedDateRange,
    setSelectedDateRange,
    runAnalysis,
    clearAnalysis,
    clearCacheAndReload
  };
};
