import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, Calendar, X, Loader2 } from 'lucide-react';
import RunAnalysisSection from '../components/portfolio/RunAnalysisSection';
import PortfolioMetricsDisplay from '../components/portfolio/PortfolioMetricsDisplay';
// TickerAnalysisDisplay removed - ticker analysis will be separate feature
import DataWarnings from '../components/portfolio/DataWarnings';
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
      } catch {
        // Portfolio loading error is handled by the error state
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
        } catch {
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

        {/* Analysis Results */}
        {analysisResults && (
          <div className="space-y-6">
            {/* Data Warnings */}
            {analysisResults.dataWarnings && (
              <DataWarnings warnings={analysisResults.dataWarnings} />
            )}

            {/* Portfolio Metrics */}
            <PortfolioMetricsDisplay 
              metrics={analysisResults.portfolioMetrics} 
              timeSeriesData={analysisResults.timeSeriesData}
            />
          </div>
        )}

        {/* Legend Sidebar */}
        {showLegend && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                setShowLegend(false);
              }
            }}
          >
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] flex flex-col">
              {/* Fixed Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
                <h2 className="text-2xl font-semibold text-gray-900">Metrics Legend</h2>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setShowLegend(false);
                  }}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-md hover:bg-gray-100 cursor-pointer"
                  aria-label="Close legend"
                  type="button"
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
