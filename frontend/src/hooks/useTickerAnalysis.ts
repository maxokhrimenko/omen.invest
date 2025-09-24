import { useState, useCallback, useEffect } from 'react';
import type { DateRange } from '../components/portfolio/DateRangeSelector';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import { useToast } from '../contexts/ToastContext';
import { calculateAnalysisTimeout, formatTimeout } from '../utils/timeoutCalculator';
import type { TickerAnalysis } from '../types/portfolio';

export interface DataWarnings {
  missingTickers: string[];
  tickersWithoutStartData: string[];
  firstAvailableDates: { [ticker: string]: string };
}

export interface TickerAnalysisResults {
  tickerMetrics: TickerAnalysis[];
  failedTickers: Array<{ ticker: string; firstAvailableDate?: string }>;
  dataWarnings: DataWarnings;
  analysisDate: string;
  dateRange: DateRange;
}

export const useTickerAnalysis = () => {
  const [analysisResults, setAnalysisResults] = useState<TickerAnalysisResults | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('cards');
  const { showToast, hideToast } = useToast();

  // Load analysis results from localStorage on mount
  useEffect(() => {
    const savedResults = localStorage.getItem('tickerAnalysisResults');
    const savedDateRange = localStorage.getItem('tickerAnalysisDateRange');
    const savedViewMode = localStorage.getItem('tickerAnalysisViewMode');
    
    if (savedResults) {
      try {
        setAnalysisResults(JSON.parse(savedResults));
      } catch (error) {
        console.error('Failed to parse saved ticker analysis results:', error);
        localStorage.removeItem('tickerAnalysisResults');
      }
    }
    
    if (savedDateRange) {
      try {
        setSelectedDateRange(JSON.parse(savedDateRange));
      } catch (error) {
        console.error('Failed to parse saved date range:', error);
        localStorage.removeItem('tickerAnalysisDateRange');
      }
    }

    if (savedViewMode) {
      try {
        setViewMode(JSON.parse(savedViewMode) as 'table' | 'cards');
      } catch (error) {
        console.error('Failed to parse saved view mode:', error);
        localStorage.removeItem('tickerAnalysisViewMode');
      }
    }
  }, []);

  // Save analysis results to localStorage
  const saveAnalysisResults = useCallback((results: TickerAnalysisResults) => {
    localStorage.setItem('tickerAnalysisResults', JSON.stringify(results));
  }, []);

  // Save view mode to localStorage
  const saveViewMode = useCallback((mode: 'table' | 'cards') => {
    localStorage.setItem('tickerAnalysisViewMode', JSON.stringify(mode));
  }, []);

  // Clear analysis results
  const clearAnalysis = useCallback(() => {
    setAnalysisResults(null);
    setError(null);
    localStorage.removeItem('tickerAnalysisResults');
    localStorage.removeItem('tickerAnalysisDateRange');
    localStorage.removeItem('tickerAnalysisViewMode');
  }, []);

  // Update view mode
  const updateViewMode = useCallback((mode: 'table' | 'cards') => {
    setViewMode(mode);
    saveViewMode(mode);
  }, [saveViewMode]);

  // Run ticker analysis
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
      title: 'Ticker Analysis in Progress',
      message: `Analyzing individual tickers${estimatedTimeText}...`,
      persistent: true
    });

    try {
      logger.info('Starting ticker analysis', { 
        operation: 'ticker_analysis',
        startDate, 
        endDate, 
        tickerCount 
      });
      
      // Call ticker analysis API endpoint
      const tickerResponse = await apiService.analyzeTickers(startDate, endDate, tickerCount);

      logger.info('API response received', { 
        operation: 'api_responses',
        tickerSuccess: true, 
        tickerCount: tickerResponse.data.length,
        failedTickers: tickerResponse.failedTickers?.length || 0
      });

      // Convert API response to our internal format
      const results: TickerAnalysisResults = {
        tickerMetrics: tickerResponse.data,
        failedTickers: tickerResponse.failedTickers || [],
        dataWarnings: {
          missingTickers: tickerResponse.warnings?.missingTickers || [],
          tickersWithoutStartData: tickerResponse.warnings?.tickersWithoutStartData || [],
          firstAvailableDates: tickerResponse.warnings?.firstAvailableDates || {}
        },
        analysisDate: new Date().toISOString(),
        dateRange: {
          startDate,
          endDate,
          label: `${startDate} to ${endDate}`,
          type: 'custom' as const
        }
      };

      setAnalysisResults(results);
      saveAnalysisResults(results);

      // Hide loading toast and show success
      hideToast(loadingToastId);
      showToast({
        type: 'success',
        title: 'Analysis Complete',
        message: `Successfully analyzed ${tickerResponse.data.length} tickers`,
        duration: 3000
      });

      logger.info('Ticker analysis completed successfully', {
        operation: 'ticker_analysis',
        tickerCount: tickerResponse.data.length,
        failedTickers: tickerResponse.failedTickers?.length || 0
      });

    } catch (error: any) {
      logger.error('Ticker analysis failed', error, {
        operation: 'ticker_analysis',
        startDate,
        endDate,
        tickerCount
      });

      setError(error.message || 'Ticker analysis failed');
      
      // Hide loading toast and show error
      hideToast(loadingToastId);
      showToast({
        type: 'error',
        title: 'Analysis Failed',
        message: error.message || 'Failed to analyze tickers',
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  }, [showToast, hideToast, saveAnalysisResults, logger]);

  return {
    analysisResults,
    isLoading,
    error,
    selectedDateRange,
    setSelectedDateRange,
    viewMode,
    setViewMode: updateViewMode,
    runAnalysis,
    clearAnalysis
  };
};
