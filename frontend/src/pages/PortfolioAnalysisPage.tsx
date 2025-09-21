import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, Calendar, X, Loader2 } from 'lucide-react';
import DateRangeSelector from '../components/portfolio/DateRangeSelector';
import AnalysisTrigger from '../components/portfolio/AnalysisTrigger';
import RedesignedPortfolioMetrics from '../components/portfolio/RedesignedPortfolioMetrics';
import TickerAnalysisDisplay from '../components/portfolio/TickerAnalysisDisplay';
import DataAvailabilityWarnings from '../components/portfolio/DataAvailabilityWarnings';
import MetricsLegend from '../components/portfolio/MetricsLegend';
import { usePortfolioAnalysis } from '../hooks/usePortfolioAnalysis';
import { apiService } from '../services/api';

interface Portfolio {
  positions: Array<{
    ticker: string;
    position: number;
  }>;
  totalPositions: number;
  tickers: string[];
}

const PortfolioAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [showLegend, setShowLegend] = useState(false);
  
  const {
    analysisResults,
    isLoading,
    error,
    selectedDateRange,
    setSelectedDateRange,
    runAnalysis,
    clearAnalysis
  } = usePortfolioAnalysis();

  // Load portfolio from backend
  useEffect(() => {
    const loadPortfolio = async () => {
      try {
        const portfolioData = await apiService.getPortfolio();
        if (portfolioData) {
          setPortfolio(portfolioData);
          
          // Also save to localStorage for consistency
          localStorage.setItem('portfolio', JSON.stringify(portfolioData));
        } else {
          // No portfolio loaded, redirect to upload page
          navigate('/');
        }
      } catch (error) {
        console.error('Failed to load portfolio from backend:', error);
        navigate('/');
      }
    };
    
    loadPortfolio();
  }, [navigate]);

  // Refresh portfolio when returning to this page (e.g., after uploading new portfolio)
  useEffect(() => {
    const handleFocus = () => {
      const loadPortfolio = async () => {
        try {
          const portfolioData = await apiService.getPortfolio();
          if (portfolioData) {
            setPortfolio(portfolioData);
            localStorage.setItem('portfolio', JSON.stringify(portfolioData));
          } else {
            // No portfolio loaded, redirect to upload page
            navigate('/');
          }
        } catch (error) {
          // If portfolio doesn't exist, redirect to upload page
          navigate('/');
        }
      };
      loadPortfolio();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [navigate]);

  // Redirect if no portfolio
  if (!portfolio) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  const handleAnalysis = async (startDate: string, endDate: string) => {
    await runAnalysis(startDate, endDate, portfolio?.tickers.length);
  };

  const handleClearAnalysis = () => {
    clearAnalysis();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1 flex items-center">
              <BarChart3 className="w-8 h-8 mr-2 text-blue-600" />
              Portfolio Analysis
            </h1>
            <p className="text-lg text-gray-600">
              Analyze your portfolio performance
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowLegend(!showLegend)}
              className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Calendar className="w-4 h-4 mr-1" />
              {showLegend ? 'Hide' : 'Show'} Legend
            </button>
          </div>
        </div>

        {/* Portfolio Summary */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Portfolio Summary</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{portfolio.tickers.length}</div>
              <div className="text-xs text-gray-500">Tickers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{portfolio.totalPositions.toLocaleString()}</div>
              <div className="text-xs text-gray-500">Positions</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${analysisResults ? 'text-purple-600' : 'text-gray-400'}`}>
                {analysisResults ? '✓' : '○'}
              </div>
              <div className="text-xs text-gray-500">Status</div>
            </div>
          </div>
        </div>

        {/* Run New Analysis Section - Always on top */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Run Analysis</h2>
                </div>
          
          {/* Three Horizontal Blocks */}
          <div className="flex items-start space-x-6">
            {/* Block 1: Predefined Periods */}
            <div className="flex-1">
              <DateRangeSelector
                selectedRange={selectedDateRange}
                onRangeChange={setSelectedDateRange}
              />
            </div>
            
            {/* Block 2: Analysis Button */}
            <div className="w-48">
              <AnalysisTrigger
                onAnalyze={handleAnalysis}
                onClearResults={handleClearAnalysis}
                isLoading={isLoading}
                selectedDateRange={selectedDateRange}
                error={error}
                hasResults={!!analysisResults}
                tickerCount={portfolio?.tickers.length}
              />
            </div>
          </div>
        </div>

        {/* Analysis Results */}
        {analysisResults && (
          <div className="space-y-6">
            {/* Data Availability Warnings */}
            {analysisResults.dataAvailabilityWarnings && (
              <DataAvailabilityWarnings warnings={analysisResults.dataAvailabilityWarnings} />
            )}

            {/* Portfolio Metrics */}
            <RedesignedPortfolioMetrics 
              metrics={analysisResults.portfolioMetrics} 
              timeSeriesData={analysisResults.timeSeriesData}
            />

            {/* Individual Ticker Analysis */}
            <TickerAnalysisDisplay tickerMetrics={analysisResults.tickerMetrics} />
          </div>
        )}

        {/* Legend Sidebar */}
        {showLegend && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] flex flex-col">
              {/* Fixed Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
                <h2 className="text-2xl font-semibold text-gray-900">Metrics Legend</h2>
                <button
                  onClick={() => setShowLegend(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              {/* Scrollable Content */}
              <div className="overflow-y-auto flex-1">
                <div className="p-6">
                  <MetricsLegend />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioAnalysisPage;
