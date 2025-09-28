import React, { useMemo, useCallback } from 'react';
import { Trophy, TrendingDown, BarChart3, Shield, AlertTriangle } from 'lucide-react';
import type { TickerAnalysis, TickerComparisonData } from '../../types/portfolio';
import { getMetricColorClasses, parseMetricValue } from '../../utils/tickerColorCoding';

interface ComparisonCardsProps {
  tickerMetrics: TickerAnalysis[];
  bestPerformer: TickerComparisonData;
  worstPerformer: TickerComparisonData;
  bestSharpe: TickerComparisonData;
  lowestRisk: TickerComparisonData;
  problematicTickers?: string[];
  firstAvailableDates?: { [ticker: string]: string };
}

const ComparisonCards: React.FC<ComparisonCardsProps> = ({
  tickerMetrics,
  bestPerformer,
  worstPerformer,
  bestSharpe,
  lowestRisk,
  problematicTickers = [],
  firstAvailableDates = {}
}) => {
  // Helper function to check if ticker has data issues
  const isProblematicTicker = useCallback((ticker: string) => {
    return problematicTickers.includes(ticker);
  }, [problematicTickers]);

  // Helper function to get warning message for problematic ticker
  const getWarningMessage = useCallback((ticker: string) => {
    if (!isProblematicTicker(ticker)) return null;
    const firstDate = firstAvailableDates[ticker];
    return firstDate 
      ? `Data available from ${firstDate} (partial period analysis)`
      : 'Incomplete data for selected period';
  }, [isProblematicTicker, firstAvailableDates]);

  // Color coding function
  const getMetricColor = useCallback((value: string | undefined, metricName: string) => {
    if (!value || value === 'N/A') return 'text-gray-400';
    
    const numValue = parseMetricValue(value);
    if (numValue === null) return 'text-gray-400';
    
    return getMetricColorClasses(metricName, numValue);
  }, []);

  // Get performance badges
  const getPerformanceBadges = useCallback((ticker: string) => {
    const badges = [];
    
    if (ticker === bestPerformer.ticker) {
      badges.push({ icon: Trophy, label: 'Best', color: 'bg-green-100 text-green-800' });
    }
    if (ticker === worstPerformer.ticker) {
      badges.push({ icon: TrendingDown, label: 'Worst', color: 'bg-red-100 text-red-800' });
    }
    if (ticker === bestSharpe.ticker) {
      badges.push({ icon: BarChart3, label: 'Sharpe', color: 'bg-blue-100 text-blue-800' });
    }
    if (ticker === lowestRisk.ticker) {
      badges.push({ icon: Shield, label: 'Low Risk', color: 'bg-purple-100 text-purple-800' });
    }
    
    return badges;
  }, [bestPerformer.ticker, worstPerformer.ticker, bestSharpe.ticker, lowestRisk.ticker]);

  // Sort by annualized return (best performers first)
  const sortedMetrics = useMemo(() => {
    return [...tickerMetrics].sort((a, b) => {
      const aValue = parseFloat(a.annualizedReturn.replace(/[%,$]/g, ''));
      const bValue = parseFloat(b.annualizedReturn.replace(/[%,$]/g, ''));
      return bValue - aValue; // Descending order
    });
  }, [tickerMetrics]);

  if (!tickerMetrics || tickerMetrics.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8 text-center">
        <div className="text-gray-500 text-lg">No ticker data available</div>
        <div className="text-gray-400 text-sm mt-2">Run comparison to see ticker metrics</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {sortedMetrics.map((ticker) => {
          const badges = getPerformanceBadges(ticker.ticker);
          const isProblematic = isProblematicTicker(ticker.ticker);
          const warningMessage = getWarningMessage(ticker.ticker);
          
          return (
            <div key={ticker.ticker} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 hover:shadow-md transition-shadow">
              {/* Ticker Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isProblematic ? 'bg-amber-100' : 'bg-primary-100'
                  }`}>
                    <span className={`text-sm font-bold ${
                      isProblematic ? 'text-amber-700' : 'text-primary-700'
                    }`}>
                      {ticker.ticker.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {ticker.ticker}
                      </h3>
                      {isProblematic && (
                        <div className="group relative">
                          <AlertTriangle className="w-4 h-4 text-amber-500" />
                          {warningMessage && (
                            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                              <div className="bg-amber-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap">
                                {warningMessage}
                                <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-2 border-r-2 border-t-2 border-transparent border-t-amber-900"></div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    {ticker.position && (
                      <p className="text-sm text-gray-500">Position: {ticker.position}</p>
                    )}
                  </div>
                </div>
                
                {/* Performance Badges */}
                <div className="flex flex-wrap gap-1">
                  {badges.map((badge, index) => {
                    const Icon = badge.icon;
                    return (
                      <span
                        key={index}
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}
                      >
                        <Icon className="w-3 h-3 mr-1" />
                        {badge.label}
                      </span>
                    );
                  })}
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1">Annual Return</div>
                  <div className={`text-lg font-bold ${getMetricColor(ticker.annualizedReturn, 'annualizedReturn')}`}>
                    {ticker.annualizedReturn}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1">Sharpe Ratio</div>
                  <div className={`text-lg font-bold ${getMetricColor(ticker.sharpeRatio, 'sharpeRatio')}`}>
                    {ticker.sharpeRatio}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1">Volatility</div>
                  <div className={`text-lg font-bold ${getMetricColor(ticker.volatility, 'volatility')}`}>
                    {ticker.volatility}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1">Max Drawdown</div>
                  <div className={`text-lg font-bold ${getMetricColor(ticker.maxDrawdown, 'maxDrawdown')}`}>
                    {ticker.maxDrawdown}
                  </div>
                </div>
              </div>

              {/* Additional Metrics */}
              <div className="border-t border-gray-100 pt-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-xs font-medium text-gray-500 mb-1">Total Return</div>
                    <div className={`font-medium ${getMetricColor(ticker.totalReturn, 'totalReturn')}`}>
                      {ticker.totalReturn}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-gray-500 mb-1">Beta</div>
                    <div className={`font-medium ${getMetricColor(ticker.beta, 'beta')}`}>
                      {ticker.beta}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-gray-500 mb-1">Sortino Ratio</div>
                    <div className={`font-medium ${getMetricColor(ticker.sortinoRatio, 'sortinoRatio')}`}>
                      {ticker.sortinoRatio}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-gray-500 mb-1">VaR 95%</div>
                    <div className={`font-medium ${getMetricColor(ticker.var95, 'var95')}`}>
                      {ticker.var95}
                    </div>
                  </div>
                </div>
              </div>

              {/* Market Value */}
              {ticker.marketValue && (
                <div className="border-t border-gray-100 pt-4 mt-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-500">Market Value</span>
                    <span className="text-lg font-bold text-gray-900">{ticker.marketValue}</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ComparisonCards;
