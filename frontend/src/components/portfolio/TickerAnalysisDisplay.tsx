import React, { useState, useMemo, useCallback } from 'react';
import { ChevronDown, ChevronRight, TrendingUp, TrendingDown, DollarSign, Calendar } from 'lucide-react';

// Temporary interface for ticker analysis (will be moved to separate feature later)
interface TickerMetrics {
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

interface TickerAnalysisDisplayProps {
  tickerMetrics: TickerMetrics[];
}

const TickerAnalysisDisplay: React.FC<TickerAnalysisDisplayProps> = ({ tickerMetrics }) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [sortField, setSortField] = useState<keyof TickerMetrics>('ticker');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const toggleRow = useCallback((ticker: string) => {
    setExpandedRows(prev => {
      const newExpanded = new Set(prev);
      if (newExpanded.has(ticker)) {
        newExpanded.delete(ticker);
      } else {
        newExpanded.add(ticker);
      }
      return newExpanded;
    });
  }, []);

  const handleSort = useCallback((field: keyof TickerMetrics) => {
    setSortField(field);
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
  }, []);

  const sortedMetrics = useMemo(() => {
    return [...tickerMetrics].sort((a, b) => {
      const aField = a[sortField];
      const bField = b[sortField];
      
      // Handle undefined or null values
      if (!aField || !bField) {
        if (!aField && !bField) return 0;
        if (!aField) return 1;
        if (!bField) return -1;
      }
      
      const aValue = parseFloat(aField.replace(/[%,$]/g, ''));
      const bValue = parseFloat(bField.replace(/[%,$]/g, ''));
      
      if (isNaN(aValue) || isNaN(bValue)) {
        return aField.localeCompare(bField);
      }
      
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });
  }, [tickerMetrics, sortField, sortDirection]);

  const getColorClass = useCallback((value: string | undefined, type: 'return' | 'risk' | 'ratio') => {
    if (!value) return 'text-gray-400';
    
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    
    if (isNaN(numValue)) return 'text-gray-400';
    
    if (type === 'return') {
      if (numValue < 5) return 'text-red-600';
      if (numValue > 20) return 'text-green-600';
      return 'text-yellow-600';
    } else if (type === 'risk') {
      if (numValue > 50) return 'text-red-600';
      if (numValue < 30) return 'text-green-600';
      return 'text-yellow-600';
    } else if (type === 'ratio') {
      if (numValue < 0.5) return 'text-red-600';
      if (numValue > 1.5) return 'text-green-600';
      return 'text-yellow-600';
    }
    
    return 'text-gray-600';
  }, []);

  const getFrequencyIcon = useCallback((frequency: string) => {
    switch (frequency) {
      case 'Monthly': return '🟢';
      case 'Quarterly': return '🔵';
      case 'Semi-Annual': return '🟡';
      case 'Annual': return '🟠';
      case 'Irregular': return '🔴';
      default: return '⚪';
    }
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Individual Ticker Analysis</h2>
        <div className="text-sm text-gray-500">
          {tickerMetrics.length} tickers analyzed
        </div>
      </div>

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
                Ann. Return
                {sortField === 'annualizedReturn' && (
                  <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('volatility')}
              >
                Volatility
                {sortField === 'volatility' && (
                  <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('sharpeRatio')}
              >
                Sharpe
                {sortField === 'sharpeRatio' && (
                  <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('maxDrawdown')}
              >
                Max DD
                {sortField === 'maxDrawdown' && (
                  <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('dividendYield')}
              >
                Div. Yield
                {sortField === 'dividendYield' && (
                  <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedMetrics.map((ticker) => (
              <React.Fragment key={ticker.ticker}>
                <tr className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                        <span className="text-xs font-medium text-blue-700">
                          {ticker.ticker.charAt(0)}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-900">{ticker.ticker}</span>
                    </div>
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getColorClass(ticker.annualizedReturn, 'return')}`}>
                    {ticker.annualizedReturn || 'N/A'}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getColorClass(ticker.volatility, 'risk')}`}>
                    {ticker.volatility || 'N/A'}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getColorClass(ticker.sharpeRatio, 'ratio')}`}>
                    {ticker.sharpeRatio || 'N/A'}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getColorClass(ticker.maxDrawdown, 'risk')}`}>
                    {ticker.maxDrawdown || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    <div className="flex items-center">
                      <span className="mr-1">{getFrequencyIcon(ticker.dividendFrequency || '')}</span>
                      {ticker.dividendYield || 'N/A'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => toggleRow(ticker.ticker)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      {expandedRows.has(ticker.ticker) ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </button>
                  </td>
                </tr>
                
                {/* Expanded Row */}
                {expandedRows.has(ticker.ticker) && (
                  <tr className="bg-gray-50">
                    <td colSpan={7} className="px-6 py-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Return Metrics */}
                        <div className="space-y-3">
                          <h4 className="font-semibold text-gray-900 flex items-center">
                            <TrendingUp className="w-4 h-4 mr-2" />
                            Returns
                          </h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Total Return:</span>
                              <span className={getColorClass(ticker.totalReturn, 'return')}>{ticker.totalReturn || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Annualized:</span>
                              <span className={getColorClass(ticker.annualizedReturn, 'return')}>{ticker.annualizedReturn || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Momentum (12-1):</span>
                              <span className={getColorClass(ticker.momentum12to1, 'return')}>{ticker.momentum12to1 || 'N/A'}</span>
                            </div>
                          </div>
                        </div>

                        {/* Risk Metrics */}
                        <div className="space-y-3">
                          <h4 className="font-semibold text-gray-900 flex items-center">
                            <TrendingDown className="w-4 h-4 mr-2" />
                            Risk
                          </h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Volatility:</span>
                              <span className={getColorClass(ticker.volatility, 'risk')}>{ticker.volatility || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Max Drawdown:</span>
                              <span className={getColorClass(ticker.maxDrawdown, 'risk')}>{ticker.maxDrawdown || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">VaR (95%):</span>
                              <span className={getColorClass(ticker.var95, 'risk')}>{ticker.var95 || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Beta:</span>
                              <span className={getColorClass(ticker.beta, 'ratio')}>{ticker.beta || 'N/A'}</span>
                            </div>
                          </div>
                        </div>

                        {/* Dividend Metrics */}
                        <div className="space-y-3">
                          <h4 className="font-semibold text-gray-900 flex items-center">
                            <DollarSign className="w-4 h-4 mr-2" />
                            Dividends
                          </h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Yield:</span>
                              <span className="text-gray-900">{ticker.dividendYield || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Amount:</span>
                              <span className="text-gray-900">{ticker.dividendAmount || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Frequency:</span>
                              <span className="text-gray-900 flex items-center">
                                <span className="mr-1">{getFrequencyIcon(ticker.dividendFrequency || '')}</span>
                                {ticker.dividendFrequency || 'N/A'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Annualized:</span>
                              <span className="text-gray-900">{ticker.annualizedDividend || 'N/A'}</span>
                            </div>
                          </div>
                        </div>

                        {/* Price Information */}
                        <div className="space-y-3">
                          <h4 className="font-semibold text-gray-900 flex items-center">
                            <Calendar className="w-4 h-4 mr-2" />
                            Prices
                          </h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Start Price:</span>
                              <span className="text-gray-900">{ticker.startPrice || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">End Price:</span>
                              <span className="text-gray-900">{ticker.endPrice || 'N/A'}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TickerAnalysisDisplay;
