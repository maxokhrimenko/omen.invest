import { useState, useEffect, useCallback } from 'react';
import type { DateRange } from '../components/portfolio/DateRangeSelector';
import { apiService } from '../services/api';

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
  momentum12_1: string;
  dividendYield: string;
  dividendAmount: string;
  dividendFrequency: string;
  annualizedDividend: string;
  startPrice: string;
  endPrice: string;
}

export interface DataAvailabilityWarnings {
  missingTickers: string[];
  tickersWithoutStartData: string[];
  firstAvailableDates: { [ticker: string]: string };
}

export interface AnalysisResults {
  portfolioMetrics: PortfolioMetrics;
  tickerMetrics: TickerMetrics[];
  dataAvailabilityWarnings: DataAvailabilityWarnings;
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

  // Load saved analysis results from localStorage
  useEffect(() => {
    const savedResults = localStorage.getItem('portfolioAnalysisResults');
    const savedDateRange = localStorage.getItem('portfolioAnalysisDateRange');
    
    if (savedResults) {
      try {
        const parsed = JSON.parse(savedResults);
        setAnalysisResults(parsed);
      } catch (error) {
        console.error('Failed to parse saved analysis results:', error);
        localStorage.removeItem('portfolioAnalysisResults');
      }
    }
    
    if (savedDateRange) {
      try {
        const parsed = JSON.parse(savedDateRange);
        setSelectedDateRange(parsed);
      } catch (error) {
        console.error('Failed to parse saved date range:', error);
        localStorage.removeItem('portfolioAnalysisDateRange');
      }
    }
  }, []);

  // Save analysis results to localStorage
  const saveAnalysisResults = useCallback((results: AnalysisResults) => {
    localStorage.setItem('portfolioAnalysisResults', JSON.stringify(results));
    localStorage.setItem('portfolioAnalysisDateRange', JSON.stringify(results.dateRange));
  }, []);

  // Clear analysis results
  const clearAnalysis = useCallback(() => {
    setAnalysisResults(null);
    setError(null);
    localStorage.removeItem('portfolioAnalysisResults');
    localStorage.removeItem('portfolioAnalysisDateRange');
  }, []);

  // Run portfolio analysis
  const runAnalysis = useCallback(async (startDate: string, endDate: string, tickerCount?: number) => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('Starting portfolio analysis...', { startDate, endDate, tickerCount });
      
      // Call real API endpoints with dynamic timeouts
      const [portfolioResponse, tickerResponseData] = await Promise.all([
        apiService.analyzePortfolio(startDate, endDate, tickerCount),
        apiService.analyzeTickers(startDate, endDate, tickerCount)
      ]);
      
      const tickerResponse = tickerResponseData.data;
      const failedTickers = tickerResponseData.failedTickers || [];

      console.log('API responses received:', { 
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
        dataAvailabilityWarnings: {
          missingTickers: portfolioResponse.warnings.missingTickers,
          tickersWithoutStartData: portfolioResponse.warnings.tickersWithoutStartData,
          firstAvailableDates: {
            // Include first available dates from successful tickers
            ...tickerResponse.reduce((acc, ticker) => {
              if (ticker.firstAvailableDate && 
                  (portfolioResponse.warnings.missingTickers.includes(ticker.ticker) || 
                   portfolioResponse.warnings.tickersWithoutStartData.includes(ticker.ticker))) {
                acc[ticker.ticker] = ticker.firstAvailableDate;
              }
              return acc;
            }, {} as { [ticker: string]: string }),
            // Include first available dates from failed tickers
            ...failedTickers.reduce((acc, failedTicker) => {
              if (failedTicker.firstAvailableDate && 
                  (portfolioResponse.warnings.missingTickers.includes(failedTicker.ticker) || 
                   portfolioResponse.warnings.tickersWithoutStartData.includes(failedTicker.ticker))) {
                acc[failedTicker.ticker] = failedTicker.firstAvailableDate;
              }
              return acc;
            }, {} as { [ticker: string]: string })
          }
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

      console.log('Analysis results created successfully:', analysisResults);
      setAnalysisResults(analysisResults);
      saveAnalysisResults(analysisResults);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      console.error('Portfolio analysis failed:', err);
      console.error('Error details:', { 
        message: errorMessage, 
        stack: err instanceof Error ? err.stack : undefined 
      });
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [selectedDateRange, saveAnalysisResults]);

  return {
    analysisResults,
    isLoading,
    error,
    selectedDateRange,
    setSelectedDateRange,
    runAnalysis,
    clearAnalysis
  };
};
