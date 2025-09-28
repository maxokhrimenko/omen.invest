import { useState, useCallback, useEffect } from 'react';
import type { DateRange } from '../components/portfolio/DateRangeSelector';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import { useToast } from './useToast';
import { calculateAnalysisTimeout, formatTimeout } from '../utils/timeoutCalculator';
import type { TickerAnalysis, TickerComparisonData } from '../types/portfolio';

export interface DataWarnings {
  missingTickers: string[];
  tickersWithoutStartData: string[];
  firstAvailableDates: { [ticker: string]: string };
}

export interface CompareTickersResults {
  tickerMetrics: TickerAnalysis[];
  bestPerformers: TickerComparisonData[];
  worstPerformers: TickerComparisonData[];
  bestSharpe: TickerComparisonData[];
  lowestRisk: TickerComparisonData[];
  failedTickers: Array<{ ticker: string; firstAvailableDate?: string }>;
  dataWarnings: DataWarnings;
  analysisDate: string;
  dateRange: DateRange;
}

export const useCompareTickers = () => {
  const [analysisResults, setAnalysisResults] = useState<CompareTickersResults | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('cards');
  const { showToast, hideToast } = useToast();

  // Load analysis results from localStorage on mount
  useEffect(() => {
    const savedResults = localStorage.getItem('compareTickersResults');
    const savedDateRange = localStorage.getItem('compareTickersDateRange');
    const savedViewMode = localStorage.getItem('compareTickersViewMode');
    
    if (savedResults) {
      try {
        const parsedResults = JSON.parse(savedResults);
        
        // Migrate old data structure to new structure
        const migratedResults: CompareTickersResults = {
          tickerMetrics: parsedResults.tickerMetrics || [],
          bestPerformers: parsedResults.bestPerformers || (parsedResults.bestPerformer ? [parsedResults.bestPerformer] : []),
          worstPerformers: parsedResults.worstPerformers || (parsedResults.worstPerformer ? [parsedResults.worstPerformer] : []),
          bestSharpe: parsedResults.bestSharpe || (parsedResults.bestSharpe ? [parsedResults.bestSharpe] : []),
          lowestRisk: parsedResults.lowestRisk || (parsedResults.lowestRisk ? [parsedResults.lowestRisk] : []),
          failedTickers: parsedResults.failedTickers || [],
          dataWarnings: parsedResults.dataWarnings || {
            missingTickers: [],
            tickersWithoutStartData: [],
            firstAvailableDates: {}
          },
          analysisDate: parsedResults.analysisDate || new Date().toISOString(),
          dateRange: parsedResults.dateRange || {
            startDate: '',
            endDate: '',
            label: '',
            type: 'custom' as const
          }
        };
        
        setAnalysisResults(migratedResults);
      } catch {
        // Clear invalid saved data
        localStorage.removeItem('compareTickersResults');
      }
    }
    
    if (savedDateRange) {
      try {
        setSelectedDateRange(JSON.parse(savedDateRange));
      } catch {
        // Clear invalid saved data
        localStorage.removeItem('compareTickersDateRange');
      }
    }

    if (savedViewMode) {
      try {
        setViewMode(JSON.parse(savedViewMode) as 'table' | 'cards');
      } catch {
        // Clear invalid saved data
        localStorage.removeItem('compareTickersViewMode');
      }
    }
  }, []);

  // Save analysis results to localStorage
  const saveAnalysisResults = useCallback((results: CompareTickersResults) => {
    localStorage.setItem('compareTickersResults', JSON.stringify(results));
  }, []);

  // Save view mode to localStorage
  const saveViewMode = useCallback((mode: 'table' | 'cards') => {
    localStorage.setItem('compareTickersViewMode', JSON.stringify(mode));
  }, []);

  // Clear analysis results
  const clearAnalysis = useCallback(() => {
    setAnalysisResults(null);
    setError(null);
    localStorage.removeItem('compareTickersResults');
    localStorage.removeItem('compareTickersDateRange');
    localStorage.removeItem('compareTickersViewMode');
  }, []);

  // Clear old data structure on mount to force fresh data
  useEffect(() => {
    const savedResults = localStorage.getItem('compareTickersResults');
    if (savedResults) {
      try {
        const parsed = JSON.parse(savedResults);
        // If old structure exists, clear it to force fresh API call
        if (parsed.bestPerformer && !parsed.bestPerformers) {
          localStorage.removeItem('compareTickersResults');
          setAnalysisResults(null);
        }
      } catch {
        // If parsing fails, clear the data
        localStorage.removeItem('compareTickersResults');
        setAnalysisResults(null);
      }
    }
  }, []);

  // Update view mode
  const updateViewMode = useCallback((mode: 'table' | 'cards') => {
    setViewMode(mode);
    saveViewMode(mode);
  }, [saveViewMode]);

  // Run ticker comparison
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
      title: 'Ticker Comparison in Progress',
      message: `Comparing tickers${estimatedTimeText}...`,
      persistent: true
    });

    try {
      logger.info('Starting ticker comparison', { 
        operation: 'compare_tickers',
        startDate, 
        endDate, 
        tickerCount 
      });
      
      // Call compare tickers API endpoint
      const response = await apiService.compareTickers(startDate, endDate, tickerCount);

      logger.info('API response received', { 
        operation: 'api_responses',
        compareSuccess: true, 
        tickerCount: response.data.metrics.length,
        bestPerformers: response.data.bestPerformers.length,
        worstPerformers: response.data.worstPerformers.length
      });

      // Convert API response to our internal format
      const results: CompareTickersResults = {
        tickerMetrics: response.data.metrics,
        bestPerformers: response.data.bestPerformers || [],
        worstPerformers: response.data.worstPerformers || [],
        bestSharpe: response.data.bestSharpe || [],
        lowestRisk: response.data.lowestRisk || [],
        failedTickers: response.failedTickers || [],
        dataWarnings: {
          missingTickers: response.warnings.missingTickers || [],
          tickersWithoutStartData: response.warnings.tickersWithoutStartData || [],
          firstAvailableDates: response.warnings.firstAvailableDates || {}
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
        title: 'Comparison Complete',
        message: `Successfully compared ${response.data.metrics.length} tickers`,
        duration: 3000
      });

      logger.info('Ticker comparison completed successfully', {
        operation: 'compare_tickers',
        tickerCount: response.data.metrics.length,
        bestPerformers: response.data.bestPerformers.length,
        worstPerformers: response.data.worstPerformers.length
      });

    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ticker comparison failed';
      logger.error('Ticker comparison failed', error instanceof Error ? error : new Error(String(error)), {
        operation: 'compare_tickers',
        startDate,
        endDate,
        tickerCount
      });

      setError(errorMessage);
      
      // Hide loading toast and show error
      hideToast(loadingToastId);
      showToast({
        type: 'error',
        title: 'Comparison Failed',
        message: errorMessage,
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  }, [showToast, hideToast, saveAnalysisResults]);

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
