import React, { useState, useEffect, useMemo } from 'react';
import { TrendingUp, AlertTriangle, RefreshCw } from 'lucide-react';
import { useTickerAnalysis } from '../hooks/useTickerAnalysis';
import { apiService } from '../services/api';
import type { Portfolio } from '../types/portfolio';
import RunAnalysisSection from '../components/portfolio/RunAnalysisSection';
import ViewToggle from '../components/portfolio/ViewToggle';
import TickerMetricsCards from '../components/portfolio/TickerMetricsCards';
import TickerMetricsTable from '../components/portfolio/TickerMetricsTable';
import DataWarnings from '../components/portfolio/DataWarnings';
import TickerFilterToggle from '../components/portfolio/TickerFilterToggle';
import ColumnVisibilityControl, { type ColumnConfig } from '../components/portfolio/ColumnVisibilityControl';
import { logger } from '../utils/logger';

// Default column configuration
const DEFAULT_COLUMNS: ColumnConfig[] = [
  { id: 'ticker', label: 'Ticker', visible: true, category: 'basic' },
  { id: 'position', label: 'Position', visible: true, category: 'basic' },
  { id: 'marketValue', label: 'Market Value', visible: true, category: 'basic' },
  { id: 'startPrice', label: 'Start', visible: false, category: 'basic' },
  { id: 'endPrice', label: 'End', visible: true, category: 'basic' },
  { id: 'totalReturn', label: 'TotRet', visible: true, category: 'returns' },
  { id: 'annualizedReturn', label: 'AnnRet', visible: true, category: 'returns' },
  { id: 'volatility', label: 'Volatility', visible: true, category: 'risk' },
  { id: 'sharpeRatio', label: 'Sharpe', visible: true, category: 'risk' },
  { id: 'maxDrawdown', label: 'MaxDD', visible: false, category: 'risk' },
  { id: 'annualizedDividend', label: 'AnnDiv', visible: true, category: 'dividends' },
  { id: 'dividendYield', label: 'DivYield', visible: true, category: 'dividends' },
  { id: 'dividendFrequency', label: 'Freq', visible: false, category: 'dividends' },
  { id: 'momentum12to1', label: 'Momentum', visible: false, category: 'other' }
];

const TickerAnalysisPage: React.FC = () => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(true);
  const [showProblematicTickers, setShowProblematicTickers] = useState(false);
  const [columnConfig, setColumnConfig] = useState<ColumnConfig[]>(DEFAULT_COLUMNS);
  
  const {
    analysisResults,
    isLoading,
    error,
    selectedDateRange,
    setSelectedDateRange,
    viewMode,
    setViewMode,
    runAnalysis,
    clearAnalysis
  } = useTickerAnalysis();

  // Column visibility handlers
  const handleColumnToggle = (columnId: string) => {
    setColumnConfig(prev => 
      prev.map(col => 
        col.id === columnId ? { ...col, visible: !col.visible } : col
      )
    );
  };

  const handleResetColumns = () => {
    setColumnConfig(DEFAULT_COLUMNS);
  };

  const handleSelectAllColumns = () => {
    setColumnConfig(prev => 
      prev.map(col => ({ ...col, visible: true }))
    );
  };

  const handleClearAllColumns = () => {
    setColumnConfig(prev => 
      prev.map(col => ({ ...col, visible: false }))
    );
  };

  // Get visible column IDs
  const visibleColumns = columnConfig
    .filter(col => col.visible)
    .map(col => col.id);

  const visibleCount = columnConfig.filter(col => col.visible).length;
  const totalCount = columnConfig.length;

  // Load portfolio on mount
  useEffect(() => {
    const loadPortfolio = async () => {
      try {
        const portfolioData = await apiService.getPortfolio();
        setPortfolio(portfolioData);
        logger.info('Portfolio loaded for ticker analysis', { 
          operation: 'portfolio_load',
          tickerCount: portfolioData?.tickers?.length || 0 
        });
      } catch (error) {
        logger.error('Failed to load portfolio for ticker analysis', error as Error);
        setPortfolio(null);
      } finally {
        setIsLoadingPortfolio(false);
      }
    };

    loadPortfolio();
  }, []);


  const handleAnalysis = async () => {
    if (!selectedDateRange) {
      logger.warn('No date range selected for ticker analysis');
      return;
    }

    if (!portfolio?.tickers?.length) {
      logger.warn('No portfolio loaded for ticker analysis');
      return;
    }

    try {
      await runAnalysis(
        selectedDateRange.startDate,
        selectedDateRange.endDate,
        portfolio.tickers.length
      );
    } catch (error) {
      logger.error('Ticker analysis failed', error as Error);
    }
  };

  const handleClearAnalysis = () => {
    clearAnalysis();
    logger.info('Ticker analysis results cleared');
  };

  // Filter tickers based on data quality
  const filteredTickerMetrics = useMemo(() => {
    if (!analysisResults?.tickerMetrics || !analysisResults?.dataWarnings) {
      return analysisResults?.tickerMetrics || [];
    }

    const problematicTickers = [
      ...analysisResults.dataWarnings.missingTickers,
      ...analysisResults.dataWarnings.tickersWithoutStartData
    ];

    if (showProblematicTickers) {
      return analysisResults.tickerMetrics;
    } else {
      return analysisResults.tickerMetrics.filter(
        ticker => !problematicTickers.includes(ticker.ticker)
      );
    }
  }, [analysisResults, showProblematicTickers]);

  // Show loading state while portfolio is loading
  if (isLoadingPortfolio) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  // Show error if no portfolio is loaded
  if (!portfolio) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto">
          <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">No Portfolio Loaded</h2>
          <p className="text-gray-600 mb-6">
            Please load a portfolio first before running ticker analysis.
          </p>
          <a
            href="/"
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
          >
            Go to Portfolio Management
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <TrendingUp className="w-8 h-8 mr-3 text-primary-600" />
                Ticker Analysis
              </h1>
              <p className="text-gray-600 mt-2">
                Analyze individual tickers in your portfolio with comprehensive metrics
              </p>
            </div>
          </div>
        </div>


        {/* Run New Analysis Section - Always on top */}
        <RunAnalysisSection
          selectedDateRange={selectedDateRange}
          onRangeChange={setSelectedDateRange}
          onAnalyze={handleAnalysis}
          onClearResults={handleClearAnalysis}
          isLoading={isLoading}
          error={error}
          hasResults={!!analysisResults}
          tickerCount={portfolio?.tickers.length}
        />

        {/* Data Availability Warnings */}
        {analysisResults?.dataWarnings && (
          <div className="mb-6">
            <DataWarnings warnings={analysisResults.dataWarnings} />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Analysis Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Display */}
        {analysisResults && (
          <div className="mb-6">
        {/* Results Header with View Toggle and Filter */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-gray-900">Ticker Analysis Results</h2>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">
              {analysisResults.tickerMetrics.length} tickers analyzed
            </div>
            
            {/* Data Quality Filter Button */}
            {analysisResults?.dataWarnings && (
              <TickerFilterToggle
                showProblematicTickers={showProblematicTickers}
                onToggle={setShowProblematicTickers}
                problematicTickerCount={
                  (analysisResults.dataWarnings.missingTickers?.length || 0) +
                  (analysisResults.dataWarnings.tickersWithoutStartData?.length || 0)
                }
                totalTickerCount={analysisResults.tickerMetrics.length}
              />
            )}
            
            <ViewToggle
              viewMode={viewMode}
              setViewMode={setViewMode}
              disabled={isLoading}
            />
            
            {/* Column Visibility Control - only show in table view */}
            {viewMode === 'table' && (
              <ColumnVisibilityControl
                columns={columnConfig}
                onColumnToggle={handleColumnToggle}
                onReset={handleResetColumns}
                onSelectAll={handleSelectAllColumns}
                onClearAll={handleClearAllColumns}
                visibleCount={visibleCount}
                totalCount={totalCount}
              />
            )}
          </div>
        </div>
            
            {viewMode === 'cards' ? (
              <TickerMetricsCards 
                tickerMetrics={filteredTickerMetrics}
                problematicTickers={[
                  ...(analysisResults.dataWarnings.missingTickers || []),
                  ...(analysisResults.dataWarnings.tickersWithoutStartData || [])
                ]}
                firstAvailableDates={analysisResults.dataWarnings.firstAvailableDates || {}}
              />
            ) : (
              <TickerMetricsTable 
                tickerMetrics={filteredTickerMetrics}
                problematicTickers={[
                  ...(analysisResults.dataWarnings.missingTickers || []),
                  ...(analysisResults.dataWarnings.tickersWithoutStartData || [])
                ]}
                firstAvailableDates={analysisResults.dataWarnings.firstAvailableDates || {}}
                visibleColumns={visibleColumns}
              />
            )}
          </div>
        )}

        {/* Empty State */}
        {!analysisResults && !isLoading && !error && (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12 text-center">
            <TrendingUp className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Analyze</h3>
            <p className="text-gray-600 mb-6">
              Select a date range and click "Run Ticker Analysis" to get started.
            </p>
            <button
              onClick={handleAnalysis}
              disabled={!selectedDateRange}
              className="px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Run Ticker Analysis
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TickerAnalysisPage;
