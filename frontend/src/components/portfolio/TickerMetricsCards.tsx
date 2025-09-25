import React, { useMemo, useCallback, useRef, useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle } from 'lucide-react';
import type { TickerAnalysis } from '../../types/portfolio';
import { getMetricColorClasses, parseMetricValue } from '../../utils/tickerColorCoding';

interface TickerMetricsCardsProps {
  tickerMetrics: TickerAnalysis[];
  problematicTickers?: string[];
  firstAvailableDates?: { [ticker: string]: string };
}

// Proper tooltip component with viewport-aware positioning
const DataWarningTooltip: React.FC<{ 
  message: string; 
  children: React.ReactNode;
}> = ({ message, children }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const updatePosition = useCallback(() => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Calculate ideal position (above the trigger, centered)
    let top = triggerRect.top - tooltipRect.height - 8;
    let left = triggerRect.left + (triggerRect.width / 2);

    // Adjust if tooltip would go off-screen
    if (left - (tooltipRect.width / 2) < 8) {
      left = 8 + (tooltipRect.width / 2);
    } else if (left + (tooltipRect.width / 2) > viewportWidth - 8) {
      left = viewportWidth - 8 - (tooltipRect.width / 2);
    }

    if (top < 8) {
      top = triggerRect.bottom + 8;
    }

    setPosition({ top, left });
  }, []);

  useEffect(() => {
    if (isVisible) {
      updatePosition();
      window.addEventListener('resize', updatePosition);
      window.addEventListener('scroll', updatePosition);
      return () => {
        window.removeEventListener('resize', updatePosition);
        window.removeEventListener('scroll', updatePosition);
      };
    }
  }, [isVisible, updatePosition]);

  return (
    <>
      <div 
        ref={triggerRef}
        className="relative group"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className="fixed z-[9999] pointer-events-none"
          style={{
            top: `${position.top}px`,
            left: `${position.left}px`,
            transform: 'translateX(-50%)'
          }}
        >
          <div className="bg-amber-900 text-white text-sm rounded-lg px-4 py-3 shadow-xl w-80 whitespace-normal">
            <div className="font-bold mb-2 text-base flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Data Warning
            </div>
            <div className="text-amber-100 leading-relaxed break-words">
              {message}
            </div>
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-amber-900"></div>
          </div>
        </div>
      )}
    </>
  );
};

const TickerMetricsCards: React.FC<TickerMetricsCardsProps> = ({ 
  tickerMetrics, 
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

  // Color coding function using proper CLI thresholds
  const getMetricColor = useCallback((value: string | undefined, metricName: string) => {
    if (!value || value === 'N/A') return 'text-gray-400';
    
    const numValue = parseMetricValue(value);
    if (numValue === null) return 'text-gray-400';
    
    return getMetricColorClasses(metricName, numValue);
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
        <div className="text-gray-400 text-sm mt-2">Run analysis to see ticker metrics</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {sortedMetrics.map((ticker) => (
          <div key={ticker.ticker} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            {/* Ticker Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  isProblematicTicker(ticker.ticker) 
                    ? 'bg-amber-100' 
                    : 'bg-primary-100'
                }`}>
                  <span className={`text-sm font-bold ${
                    isProblematicTicker(ticker.ticker)
                      ? 'text-amber-700'
                      : 'text-primary-700'
                  }`}>
                    {ticker.ticker.charAt(0)}
                  </span>
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-gray-900">{ticker.ticker}</h3>
                    {isProblematicTicker(ticker.ticker) && (
                      <DataWarningTooltip message={getWarningMessage(ticker.ticker) || ''}>
                        <AlertTriangle className="w-4 h-4 text-amber-500 cursor-help" />
                      </DataWarningTooltip>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {ticker.startPrice} → {ticker.endPrice}
                  </div>
                </div>
              </div>
            </div>

            {/* Returns Section */}
            <div className="space-y-3 mb-4">
              <h4 className="font-semibold text-gray-900 flex items-center">
                <TrendingUp className="w-4 h-4 mr-2" />
                Returns
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Return:</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.totalReturn, 'totalReturn')}`}>
                    {ticker.totalReturn || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Annualized:</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.annualizedReturn, 'annualizedReturn')}`}>
                    {ticker.annualizedReturn || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Momentum (12-1):</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.momentum12to1, 'momentum12to1')}`}>
                    {ticker.momentum12to1 || 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            {/* Risk Section */}
            <div className="space-y-3 mb-4">
              <h4 className="font-semibold text-gray-900 flex items-center">
                <TrendingDown className="w-4 h-4 mr-2" />
                Risk
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Volatility:</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.volatility, 'volatility')}`}>
                    {ticker.volatility || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Max Drawdown:</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.maxDrawdown, 'maxDrawdown')}`}>
                    {ticker.maxDrawdown || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">VaR (95%):</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.var95, 'var95')}`}>
                    {ticker.var95 || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Beta:</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.beta, 'beta')}`}>
                    {ticker.beta || 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            {/* Dividends Section */}
            <div className="space-y-3">
              <h4 className="font-semibold text-gray-900 flex items-center">
                <DollarSign className="w-4 h-4 mr-2" />
                Dividends
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Yield:</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${getMetricColor(ticker.dividendYield, 'dividendYield')}`}>
                    {ticker.dividendYield || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Amount:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {ticker.dividendAmount || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Frequency:</span>
                  <span className="text-sm font-medium text-gray-900 flex items-center">
                    <span className="mr-1">{getFrequencyIcon(ticker.dividendFrequency || '')}</span>
                    {ticker.dividendFrequency || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Annualized:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {ticker.annualizedDividend || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TickerMetricsCards;
