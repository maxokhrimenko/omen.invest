import { useState, useCallback } from 'react';
import type { DateRange } from '../components/portfolio/DateRangeSelector';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import { useToast } from '../contexts/ToastContext';
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
}

export interface TickerMetrics {
  ticker: string;
  totalReturn: string;
  annualizedReturn: string;
  volatility: string;
  sharpeRatio: string;
  maxDrawdown: string;
  sortinoRatio: string;
  beta: string;
  var95: string;
  momentum12to1: string;
  dividendYield: string;
  dividendAmount: string;
  dividendFrequency: string;
  annualizedDividend: string;
  startPrice: string;
  endPrice: string;
}

export interface DataWarnings {
  missingTickers: string[];
  tickersWithoutStartData: string[];
  firstAvailableDates: { [ticker: string]: string };
}

export interface AnalysisResults {
  portfolioMetrics: PortfolioMetrics;
  tickerMetrics: TickerMetrics[];
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

  // No localStorage caching - rely on warehouse system for data persistence
  // This ensures fresh data and eliminates cache inconsistency issues
  const saveAnalysisResults = useCallback((_results: AnalysisResults) => {
    // Analysis results are not cached - always fetch fresh data from warehouse
  }, []);

  // Clear analysis results
  const clearAnalysis = useCallback(() => {
    setAnalysisResults(null);
    setError(null);
  }, []);

  // Clear cache and reload data (no-op since we don't use cache)
  const clearCacheAndReload = useCallback(() => {
    console.log('Cache clearing not needed - using warehouse system for data persistence');
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
      message: `Analyzing ${tickerCount || 'portfolio'} tickers${estimatedTimeText}...`,
      persistent: true
    });

    try {
      logger.info('Starting portfolio analysis', { 
        operation: 'portfolio_analysis',
        startDate, 
        endDate, 
        tickerCount 
      });
      
      // Call real API endpoints with dynamic timeouts
      const [portfolioResponse, tickerResponseData] = await Promise.all([
        apiService.analyzePortfolio(startDate, endDate, tickerCount),
        apiService.analyzeTickers(startDate, endDate, tickerCount)
      ]);
      
      const tickerResponse = tickerResponseData.data;

      logger.info('API responses received', { 
        operation: 'api_responses',
        portfolioSuccess: portfolioResponse.success, 
        portfolioData: portfolioResponse.data,
        tickerCount: tickerResponse.length 
      });

      if (!portfolioResponse.success) {
        throw new Error(portfolioResponse.message);
      }

      // Convert API responses to our internal format
      const analysisResults: AnalysisResults = {
        portfolioMetrics: portfolioResponse.data,
        tickerMetrics: tickerResponse,
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
        tickerCount: analysisResults.tickerMetrics.length,
        hasPortfolioMetrics: !!analysisResults.portfolioMetrics
      });
      setAnalysisResults(analysisResults);
      saveAnalysisResults(analysisResults);
      
      // Hide loading toast and show success toast
      hideToast(loadingToastId);
      showToast({
        type: 'success',
        title: 'Analysis Complete',
        message: `Successfully analyzed ${tickerResponse.length} tickers${estimatedTimeText}`,
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
