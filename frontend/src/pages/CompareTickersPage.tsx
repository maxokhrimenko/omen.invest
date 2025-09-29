import React, { useState, useEffect } from 'react';
import { GitCompare, BarChart3, AlertTriangle } from 'lucide-react';
import { useCompareTickers } from '../hooks/useCompareTickers';
import RunAnalysisSection from '../components/portfolio/RunAnalysisSection';
import DataWarnings from '../components/portfolio/DataWarnings';
import ComparisonSummary from '../components/portfolio/ComparisonSummary';
import AdvancedMetricsCards from '../components/portfolio/AdvancedMetricsCards';
import type { Portfolio } from '../types/portfolio';

interface CompareTickersPageProps {
  portfolio: Portfolio | null;
}

const CompareTickersPage: React.FC<CompareTickersPageProps> = ({ portfolio }) => {
  const {
    analysisResults,
    isLoading,
    error,
    selectedDateRange,
    setSelectedDateRange,
    runAnalysis,
    clearAnalysis
  } = useCompareTickers();
  const [showDataWarnings, setShowDataWarnings] = useState(false);

  // Check if portfolio is loaded
  const hasPortfolio = portfolio && portfolio.positions.length > 0;
  const tickerCount = portfolio?.tickers.length || 0;

  // Show data warnings if there are any
  useEffect(() => {
    if (analysisResults?.dataWarnings) {
      const hasWarnings = 
        analysisResults.dataWarnings.missingTickers.length > 0 ||
        analysisResults.dataWarnings.tickersWithoutStartData.length > 0;
      setShowDataWarnings(hasWarnings);
    }
  }, [analysisResults]);

  const handleRunAnalysis = async () => {
    if (!selectedDateRange) return;
    
    await runAnalysis(
      selectedDateRange.startDate,
      selectedDateRange.endDate,
      tickerCount
    );
  };

  if (!hasPortfolio) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <GitCompare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">No Portfolio Loaded</h1>
            <p className="text-gray-600 mb-6">
              Please load a portfolio first to compare tickers
            </p>
            <button
              onClick={() => window.location.href = '/portfolio-analysis'}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Go to Portfolio Analysis
            </button>
          </div>
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
                <GitCompare className="w-8 h-8 mr-3 text-primary-600" />
                Compare Tickers
              </h1>
              <p className="text-gray-600 mt-2">
                Compare {tickerCount} tickers side by side with comprehensive metrics
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {/* Clear Results button is handled by the reusable RunAnalysisSection component */}
            </div>
          </div>
        </div>

        {/* Temporary Metrics Warning */}
        <div className="mb-6">
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-amber-800 mb-1">
                  ⚠️ Metrics Calculation Notice
                </h3>
                <p className="text-sm text-amber-700 leading-relaxed">
                  Some advanced metrics on this page may display incorrect values. Our team is actively working on fixes for calculation accuracy. 
                  Please use these results with caution and refer to the main portfolio analysis for more reliable metrics.
                </p>
                <div className="mt-2 text-xs text-amber-600">
                  <strong>Affected metrics:</strong> Time Under Water, Ulcer Index, Risk Contribution, and other advanced risk metrics
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Controls */}
        <RunAnalysisSection
          selectedDateRange={selectedDateRange}
          onRangeChange={setSelectedDateRange}
          onAnalyze={handleRunAnalysis}
          onClearResults={() => {
            clearAnalysis();
            setShowDataWarnings(false);
          }}
          isLoading={isLoading}
          error={error}
          hasResults={!!analysisResults}
          tickerCount={tickerCount}
        />

        {/* Data Warnings */}
        {showDataWarnings && analysisResults && (
          <div className="mb-6">
            <DataWarnings
              warnings={analysisResults.dataWarnings}
            />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
              <span className="text-red-800 font-medium">Analysis Failed</span>
            </div>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Results */}
        {analysisResults && (
          <div className="space-y-6">
            
             {/* Summary Cards */}
             <ComparisonSummary
               bestPerformers={analysisResults.bestPerformers || []}
               worstPerformers={analysisResults.worstPerformers || []}
               bestSharpe={analysisResults.bestSharpe || []}
             />

             {/* Advanced Metrics Cards */}
             <AdvancedMetricsCards
               bestCalmar={analysisResults.bestCalmar || []}
               worstCalmar={analysisResults.worstCalmar || []}
               bestSortino={analysisResults.bestSortino || []}
               worstSortino={analysisResults.worstSortino || []}
               bestMaxDrawdown={analysisResults.bestMaxDrawdown || []}
               worstMaxDrawdown={analysisResults.worstMaxDrawdown || []}
               bestUlcer={analysisResults.bestUlcer || []}
               worstUlcer={analysisResults.worstUlcer || []}
               bestTimeUnderWater={analysisResults.bestTimeUnderWater || []}
               worstTimeUnderWater={analysisResults.worstTimeUnderWater || []}
               bestCvar={analysisResults.bestCvar || []}
               worstCvar={analysisResults.worstCvar || []}
               bestCorrelation={analysisResults.bestCorrelation || []}
               worstCorrelation={analysisResults.worstCorrelation || []}
               bestRiskContribution={analysisResults.bestRiskContribution || []}
               worstRiskContribution={analysisResults.worstRiskContribution || []}
               bestSharpe={analysisResults.bestSharpe || []}
               worstSharpe={analysisResults.bestSharpe?.slice().reverse() || []}
               bestRisk={analysisResults.lowestRisk || []}
               worstRisk={analysisResults.lowestRisk?.slice().reverse() || []}
             />
          </div>
        )}

        {/* Empty State */}
        {!analysisResults && !isLoading && (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12 text-center">
            <div className="max-w-md mx-auto">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <GitCompare className="w-10 h-10 text-blue-600" />
              </div>
              
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Compare Your Tickers
              </h2>
              
              <p className="text-gray-600 mb-8 leading-relaxed">
                Select a date range and run comparison to analyze {tickerCount} tickers 
                side by side with comprehensive performance metrics.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                  <h3 className="font-semibold text-gray-900 mb-2">Performance Comparison</h3>
                  <p className="text-sm text-gray-600">
                    Compare annual returns, Sharpe ratios, and risk metrics
                  </p>
                </div>
                
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <GitCompare className="w-8 h-8 text-green-600 mx-auto mb-3" />
                  <h3 className="font-semibold text-gray-900 mb-2">Best & Worst</h3>
                  <p className="text-sm text-gray-600">
                    Identify top performers and underperformers
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompareTickersPage;
