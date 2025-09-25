import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { AlertTriangle, Info } from 'lucide-react';
import type { TickerAnalysis } from '../../types/portfolio';
import { getMetricColorClasses, getMetricTextColor, parseMetricValue } from '../../utils/tickerColorCoding';
import { getMetricDescription } from '../../utils/metricDescriptions';

interface TickerMetricsTableProps {
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

// Tooltip component
const MetricTooltip: React.FC<{ metricName: string; children: React.ReactNode; position?: 'left' | 'center' | 'right' }> = ({ metricName, children, position = 'center' }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const description = getMetricDescription(metricName);

  if (!description) return <>{children}</>;

  // Determine positioning classes based on position prop
  const getPositionClasses = () => {
    switch (position) {
      case 'left':
        return 'left-0';
      case 'right':
        return 'right-0';
      case 'center':
      default:
        return 'left-1/2 transform -translate-x-1/2';
    }
  };

  const getArrowPositionClasses = () => {
    switch (position) {
      case 'left':
        return 'left-4';
      case 'right':
        return 'right-4';
      case 'center':
      default:
        return 'left-1/2 transform -translate-x-1/2';
    }
  };

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="cursor-help"
      >
        {children}
      </div>
      {showTooltip && (
        <div className={`absolute top-full ${getPositionClasses()} mt-2 z-50`}>
          <div className="bg-gray-900 text-white text-sm rounded-lg px-4 py-3 min-w-80 max-w-96 shadow-xl">
            <div className="font-bold mb-2 text-base">{description.name}</div>
            <div className="mb-3 text-gray-100 leading-relaxed">{description.description}</div>
            <div className="mb-2">
              <span className="text-gray-400 text-xs font-medium uppercase tracking-wide">Formula:</span>
              <div className="text-gray-200 font-mono text-sm mt-1 bg-gray-800 px-2 py-1 rounded">
                {description.formula}
              </div>
            </div>
            <div className="mb-2">
              <span className="text-gray-400 text-xs font-medium uppercase tracking-wide">Thresholds:</span>
              <div className="text-gray-200 text-sm mt-1 space-y-1">
                {description.thresholds.split(', ').map((threshold, idx) => (
                  <div key={idx} className="flex items-center">
                    <span className="text-xs mr-2">
                      {threshold.includes('Red') ? '🔴' : threshold.includes('Yellow') ? '🟡' : '🟢'}
                    </span>
                    <span>{threshold.replace(/Red |Yellow |Green /, '')}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className={`absolute -top-1 ${getArrowPositionClasses()} w-2 h-2 bg-gray-900 rotate-45`}></div>
          </div>
        </div>
      )}
    </div>
  );
};


const TickerMetricsTable: React.FC<TickerMetricsTableProps> = ({ 
  tickerMetrics, 
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

  // Color coding function using proper CLI thresholds
  const getMetricColor = useCallback((value: string | undefined, metricName: string) => {
    if (!value || value === 'N/A') return 'text-gray-400';
    
    const numValue = parseMetricValue(value);
    if (numValue === null) return 'text-gray-400';
    
    return getMetricTextColor(metricName, numValue);
  }, []);

  const getMetricBackgroundColor = useCallback((value: string | undefined, metricName: string) => {
    if (!value || value === 'N/A') return 'bg-gray-50';
    
    const numValue = parseMetricValue(value);
    if (numValue === null) return 'bg-gray-50';
    
    return getMetricColorClasses(metricName, numValue).split(' ')[1]; // Get background color
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

  const handleSort = useCallback((field: keyof TickerAnalysis) => {
    setSortField(field);
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
  }, []);

  // Helper function to determine if a field should be sorted as text
  const isTextField = useCallback((field: keyof TickerAnalysis) => {
    return field === 'ticker' || field === 'dividendFrequency';
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
      
      // For text fields, use alphabetical sorting
      if (isTextField(sortField)) {
        const aStr = String(aField).toLowerCase();
        const bStr = String(bField).toLowerCase();
        const comparison = aStr.localeCompare(bStr);
        return sortDirection === 'asc' ? comparison : -comparison;
      }
      
      // For numeric fields, parse and compare numerically
      const aValue = parseFloat(String(aField).replace(/[%,$]/g, ''));
      const bValue = parseFloat(String(bField).replace(/[%,$]/g, ''));
      
      if (isNaN(aValue) || isNaN(bValue)) {
        // Fallback to string comparison if parsing fails
        const aStr = String(aField).toLowerCase();
        const bStr = String(bField).toLowerCase();
        const comparison = aStr.localeCompare(bStr);
        return sortDirection === 'asc' ? comparison : -comparison;
      }
      
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });
  }, [tickerMetrics, sortField, sortDirection, isTextField]);

  if (!tickerMetrics || tickerMetrics.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8 text-left">
        <div className="text-gray-500 text-lg">No ticker data available</div>
        <div className="text-gray-400 text-sm mt-2">Run analysis to see ticker metrics</div>
      </div>
    );
  }

  return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                {/* First row - Metric Legends */}
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    {/* Ticker column - no legend */}
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    {/* Start $ column - no legend */}
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    {/* End $ column - no legend */}
                  </th>
                  
                  {/* TotRet */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;20%</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">5-20%</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&lt;5%</span>
                      </div>
                    </div>
                  </th>
                  
                  {/* AnnRet */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;20%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">5-20%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&lt;5%</span>
                      </div>
                    </div>
                  </th>
                  
                  {/* Volatility */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&lt;30%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">30-50%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;50%</span>
                      </div>
                    </div>
                  </th>
                  
                  {/* Sharpe */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;1.5</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">0.5-1.5</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&lt;0.5</span>
                      </div>
                    </div>
                  </th>
                  
                  {/* MaxDD */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;-30%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">-50% to -30%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;-50%</span>
                      </div>
                    </div>
                  </th>
                  
                  {/* AnnDiv */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;$4</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">$1-$4</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&lt;$1</span>
                      </div>
                    </div>
                  </th>
                  
                  {/* DivYield */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;4%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">1-4%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&lt;1%</span>
                      </div>
                    </div>
                  </th>
                  
                  {/* Freq column - no legend */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  </th>
                  
                  {/* Momentum */}
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    <div className="space-y-0.5">
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&gt;20%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">0-20%</span>
                      </div>
                      <div className="flex items-center justify-start">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                        <span className="text-gray-700 font-medium">&lt;0%</span>
                      </div>
                    </div>
                  </th>
                </tr>
                
                {/* Second row - Column Headers */}
                <tr>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('ticker')}
              >
                <div className="flex items-center">
                  Ticker
                  {sortField === 'ticker' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('startPrice')}
              >
                <div className="flex items-center">
                  Start
                  {sortField === 'startPrice' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('endPrice')}
              >
                <div className="flex items-center">
                  End
                  {sortField === 'endPrice' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('totalReturn')}
              >
                <div className="flex items-center">
                  TotRet
                  <MetricTooltip metricName="totalReturn">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'totalReturn' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('annualizedReturn')}
              >
                <div className="flex items-center">
                  AnnRet
                  <MetricTooltip metricName="annualizedReturn">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'annualizedReturn' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('volatility')}
              >
                <div className="flex items-center">
                  Volatility
                  <MetricTooltip metricName="volatility">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'volatility' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('sharpeRatio')}
              >
                <div className="flex items-center">
                  Sharpe
                  <MetricTooltip metricName="sharpeRatio">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'sharpeRatio' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('maxDrawdown')}
              >
                <div className="flex items-center">
                  MaxDD
                  <MetricTooltip metricName="maxDrawdown">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'maxDrawdown' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('annualizedDividend')}
              >
                <div className="flex items-center">
                  AnnDiv
                  <MetricTooltip metricName="annualizedDividend">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'annualizedDividend' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('dividendYield')}
              >
                <div className="flex items-center">
                  DivYield
                  <MetricTooltip metricName="dividendYield" position="right">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'dividendYield' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('dividendFrequency')}
              >
                <div className="flex items-center">
                  Freq
                  {sortField === 'dividendFrequency' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('momentum12to1')}
              >
                <div className="flex items-center">
                  Momentum
                  <MetricTooltip metricName="momentum12to1" position="right">
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                  {sortField === 'momentum12to1' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
            {sortedMetrics.map((ticker) => (
              <tr key={ticker.ticker} className="hover:bg-gray-50">
                <td className="px-3 py-3 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-2 ${
                      isProblematicTicker(ticker.ticker) 
                        ? 'bg-amber-100' 
                        : 'bg-primary-100'
                    }`}>
                      <span className={`text-xs font-medium ${
                        isProblematicTicker(ticker.ticker)
                          ? 'text-amber-700'
                          : 'text-primary-700'
                      }`}>
                        {ticker.ticker.charAt(0)}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <div className="flex items-center space-x-1">
                        <span className="text-sm font-medium text-gray-900">{ticker.ticker}</span>
                        {isProblematicTicker(ticker.ticker) && (
                          <DataWarningTooltip message={getWarningMessage(ticker.ticker) || ''}>
                            <AlertTriangle className="w-3 h-3 text-amber-500 cursor-help" />
                          </DataWarningTooltip>
                        )}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-3 py-3 whitespace-nowrap text-sm text-gray-900">
                  {ticker.startPrice || 'N/A'}
                </td>
                <td className="px-3 py-3 whitespace-nowrap text-sm text-gray-900">
                  {ticker.endPrice || 'N/A'}
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.totalReturn, 'totalReturn')} ${getMetricBackgroundColor(ticker.totalReturn, 'totalReturn')} rounded`}>
                  {ticker.totalReturn || 'N/A'}
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.annualizedReturn, 'annualizedReturn')} ${getMetricBackgroundColor(ticker.annualizedReturn, 'annualizedReturn')} rounded`}>
                  {ticker.annualizedReturn || 'N/A'}
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.volatility, 'volatility')} ${getMetricBackgroundColor(ticker.volatility, 'volatility')} rounded`}>
                  {ticker.volatility || 'N/A'}
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.sharpeRatio, 'sharpeRatio')} ${getMetricBackgroundColor(ticker.sharpeRatio, 'sharpeRatio')} rounded`}>
                  {ticker.sharpeRatio || 'N/A'}
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.maxDrawdown, 'maxDrawdown')} ${getMetricBackgroundColor(ticker.maxDrawdown, 'maxDrawdown')} rounded`}>
                  {ticker.maxDrawdown || 'N/A'}
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.annualizedDividend, 'annualizedDividend')} ${getMetricBackgroundColor(ticker.annualizedDividend, 'annualizedDividend')} rounded`}>
                  {ticker.annualizedDividend || 'N/A'}
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.dividendYield, 'dividendYield')} ${getMetricBackgroundColor(ticker.dividendYield, 'dividendYield')} rounded`}>
                  {ticker.dividendYield || 'N/A'}
                </td>
                <td className="px-3 py-3 whitespace-nowrap text-sm text-gray-900">
                  <div className="flex items-center">
                    <span className="mr-1">{getFrequencyIcon(ticker.dividendFrequency || '')}</span>
                    <span className="text-xs">{ticker.dividendFrequency || 'N/A'}</span>
                  </div>
                </td>
                <td className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(ticker.momentum12to1, 'momentum12to1')} ${getMetricBackgroundColor(ticker.momentum12to1, 'momentum12to1')} rounded`}>
                  {ticker.momentum12to1 || 'N/A'}
                </td>
              </tr>
            ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    };

export default TickerMetricsTable;
