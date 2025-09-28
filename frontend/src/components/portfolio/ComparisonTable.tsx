import React, { useState, useMemo, useCallback } from 'react';
import { Trophy, TrendingDown, BarChart3, Shield, AlertTriangle } from 'lucide-react';
import type { TickerAnalysis, TickerComparisonData } from '../../types/portfolio';
import { getMetricColorClasses, parseMetricValue } from '../../utils/tickerColorCoding';

interface ComparisonTableProps {
  tickerMetrics: TickerAnalysis[];
  bestPerformer: TickerComparisonData;
  worstPerformer: TickerComparisonData;
  bestSharpe: TickerComparisonData;
  lowestRisk: TickerComparisonData;
  problematicTickers?: string[];
  firstAvailableDates?: { [ticker: string]: string };
}

const ComparisonTable: React.FC<ComparisonTableProps> = ({
  tickerMetrics,
  bestPerformer,
  worstPerformer,
  bestSharpe,
  lowestRisk,
  problematicTickers = [],
  firstAvailableDates = {}
}) => {
  const [sortField, setSortField] = useState<keyof TickerAnalysis>('annualizedReturn');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

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

  // Sort function
  const handleSort = useCallback((field: keyof TickerAnalysis) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  }, [sortField, sortDirection]);

  // Sorted metrics
  const sortedMetrics = useMemo(() => {
    return [...tickerMetrics].sort((a, b) => {
      const aValue = parseFloat(a[sortField]?.toString().replace(/[%,$]/g, '') || '0');
      const bValue = parseFloat(b[sortField]?.toString().replace(/[%,$]/g, '') || '0');
      
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });
  }, [tickerMetrics, sortField, sortDirection]);

  if (!tickerMetrics || tickerMetrics.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8 text-center">
        <div className="text-gray-500 text-lg">No ticker data available</div>
        <div className="text-gray-400 text-sm mt-2">Run comparison to see ticker metrics</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ticker
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('annualizedReturn')}
              >
                <div className="flex items-center space-x-1">
                  <span>Annual Return</span>
                  {sortField === 'annualizedReturn' && (
                    <span className="text-gray-400">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('sharpeRatio')}
              >
                <div className="flex items-center space-x-1">
                  <span>Sharpe Ratio</span>
                  {sortField === 'sharpeRatio' && (
                    <span className="text-gray-400">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('volatility')}
              >
                <div className="flex items-center space-x-1">
                  <span>Volatility</span>
                  {sortField === 'volatility' && (
                    <span className="text-gray-400">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('maxDrawdown')}
              >
                <div className="flex items-center space-x-1">
                  <span>Max Drawdown</span>
                  {sortField === 'maxDrawdown' && (
                    <span className="text-gray-400">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedMetrics.map((ticker) => {
              const badges = getPerformanceBadges(ticker.ticker);
              const isProblematic = isProblematicTicker(ticker.ticker);
              const warningMessage = getWarningMessage(ticker.ticker);
              
              return (
                <tr key={ticker.ticker} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
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
                          <span className="text-sm font-medium text-gray-900">
                            {ticker.ticker}
                          </span>
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
                          <div className="text-xs text-gray-500">
                            Position: {ticker.position}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${getMetricColor(ticker.annualizedReturn, 'annualizedReturn')}`}>
                      {ticker.annualizedReturn}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${getMetricColor(ticker.sharpeRatio, 'sharpeRatio')}`}>
                      {ticker.sharpeRatio}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${getMetricColor(ticker.volatility, 'volatility')}`}>
                      {ticker.volatility}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${getMetricColor(ticker.maxDrawdown, 'maxDrawdown')}`}>
                      {ticker.maxDrawdown}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
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
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComparisonTable;
