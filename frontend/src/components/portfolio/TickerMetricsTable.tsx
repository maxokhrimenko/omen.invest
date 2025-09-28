import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { AlertTriangle, Info } from 'lucide-react';
import type { TickerAnalysis } from '../../types/portfolio';
import { getMetricColorClasses, getMetricTextColor, parseMetricValue } from '../../utils/tickerColorCoding';
import { getMetricDescription } from '../../utils/metricDescriptions';

interface TickerMetricsTableProps {
  tickerMetrics: TickerAnalysis[];
  problematicTickers?: string[];
  firstAvailableDates?: { [ticker: string]: string };
  visibleColumns?: string[];
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


// Column definitions
const COLUMN_DEFINITIONS = {
  ticker: { label: 'Ticker', category: 'basic' as const, required: true },
  position: { label: 'Position', category: 'basic' as const, required: false },
  marketValue: { label: 'Market Value', category: 'basic' as const, required: false },
  startPrice: { label: 'Start', category: 'basic' as const, required: false },
  endPrice: { label: 'End', category: 'basic' as const, required: false },
  totalReturn: { label: 'TotRet', category: 'returns' as const, required: false },
  annualizedReturn: { label: 'AnnRet', category: 'returns' as const, required: false },
  volatility: { label: 'Volatility', category: 'risk' as const, required: false },
  sharpeRatio: { label: 'Sharpe', category: 'risk' as const, required: false },
  maxDrawdown: { label: 'MaxDD', category: 'risk' as const, required: false },
  annualizedDividend: { label: 'AnnDiv', category: 'dividends' as const, required: false },
  dividendYield: { label: 'DivYield', category: 'dividends' as const, required: false },
  dividendFrequency: { label: 'Freq', category: 'dividends' as const, required: false },
  momentum12to1: { label: 'Momentum', category: 'other' as const, required: false }
};

const TickerMetricsTable: React.FC<TickerMetricsTableProps> = ({ 
  tickerMetrics, 
  problematicTickers = [], 
  firstAvailableDates = {},
  visibleColumns = Object.keys(COLUMN_DEFINITIONS)
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
      // Strip currency symbols, commas, and percentage signs
      const aValue = parseFloat(String(aField).replace(/[%,$]/g, '').replace(/,/g, ''));
      const bValue = parseFloat(String(bField).replace(/[%,$]/g, '').replace(/,/g, ''));
      
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
                  {visibleColumns.map((columnId) => {
                    const column = COLUMN_DEFINITIONS[columnId as keyof typeof COLUMN_DEFINITIONS];
                    if (!column) return null;
                    
                    // Only show legends for certain columns
                    const showLegend = ['totalReturn', 'annualizedReturn', 'volatility', 'sharpeRatio', 'maxDrawdown', 'annualizedDividend', 'dividendYield', 'momentum12to1'].includes(columnId);
                    
                    return (
                      <th key={columnId} className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                        {showLegend ? (
                    <div className="space-y-0.5">
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                              <span className="text-gray-700 font-medium">
                                {columnId === 'totalReturn' || columnId === 'annualizedReturn' ? '>20%' :
                                 columnId === 'volatility' ? '<30%' :
                                 columnId === 'sharpeRatio' ? '>1.5' :
                                 columnId === 'maxDrawdown' ? '>-30%' :
                                 columnId === 'annualizedDividend' ? '>$4' :
                                 columnId === 'dividendYield' ? '>4%' :
                                 columnId === 'momentum12to1' ? '>20%' : ''}
                              </span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                              <span className="text-gray-700 font-medium">
                                {columnId === 'totalReturn' || columnId === 'annualizedReturn' ? '5-20%' :
                                 columnId === 'volatility' ? '30-50%' :
                                 columnId === 'sharpeRatio' ? '0.5-1.5' :
                                 columnId === 'maxDrawdown' ? '-50% to -30%' :
                                 columnId === 'annualizedDividend' ? '$1-$4' :
                                 columnId === 'dividendYield' ? '1-4%' :
                                 columnId === 'momentum12to1' ? '0-20%' : ''}
                              </span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                              <span className="text-gray-700 font-medium">
                                {columnId === 'totalReturn' || columnId === 'annualizedReturn' ? '<5%' :
                                 columnId === 'volatility' ? '>50%' :
                                 columnId === 'sharpeRatio' ? '<0.5' :
                                 columnId === 'maxDrawdown' ? '>-50%' :
                                 columnId === 'annualizedDividend' ? '<$1' :
                                 columnId === 'dividendYield' ? '<1%' :
                                 columnId === 'momentum12to1' ? '<0%' : ''}
                              </span>
                      </div>
                    </div>
                        ) : (
                          <div></div>
                        )}
                  </th>
                    );
                  })}
                </tr>
                
                {/* Second row - Column Headers */}
                <tr>
                  {visibleColumns.map((columnId) => {
                    const column = COLUMN_DEFINITIONS[columnId as keyof typeof COLUMN_DEFINITIONS];
                    if (!column) return null;
                    
                    const hasTooltip = ['totalReturn', 'annualizedReturn', 'volatility', 'sharpeRatio', 'maxDrawdown', 'annualizedDividend', 'dividendYield', 'momentum12to1'].includes(columnId);
                    
                    return (
                      <th 
                        key={columnId}
                className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        onClick={() => handleSort(columnId as keyof TickerAnalysis)}
              >
                <div className="flex items-center">
                          {column.label}
                          {hasTooltip && (
                            <MetricTooltip metricName={columnId} position={['dividendYield', 'momentum12to1'].includes(columnId) ? 'right' : 'center'}>
                    <Info className="w-3 h-3 ml-1" />
                  </MetricTooltip>
                          )}
                          {sortField === columnId && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
            {sortedMetrics.map((ticker) => (
              <tr key={ticker.ticker} className="hover:bg-gray-50">
                {visibleColumns.map((columnId) => {
                  const column = COLUMN_DEFINITIONS[columnId as keyof typeof COLUMN_DEFINITIONS];
                  if (!column) return null;
                  
                  const value = ticker[columnId as keyof TickerAnalysis];
                  const isMetricColumn = ['totalReturn', 'annualizedReturn', 'volatility', 'sharpeRatio', 'maxDrawdown', 'annualizedDividend', 'dividendYield', 'momentum12to1'].includes(columnId);
                  
                  if (columnId === 'ticker') {
                    return (
                      <td key={columnId} className="px-3 py-3 whitespace-nowrap">
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
                    );
                  }
                  
                  if (columnId === 'dividendFrequency') {
                    return (
                      <td key={columnId} className="px-3 py-3 whitespace-nowrap text-sm text-gray-900">
                  <div className="flex items-center">
                    <span className="mr-1">{getFrequencyIcon(ticker.dividendFrequency || '')}</span>
                    <span className="text-xs">{ticker.dividendFrequency || 'N/A'}</span>
                  </div>
                </td>
                    );
                  }
                  
                  if (isMetricColumn) {
                    return (
                      <td key={columnId} className={`px-3 py-3 whitespace-nowrap text-sm font-medium ${getMetricColor(value as string, columnId)} ${getMetricBackgroundColor(value as string, columnId)} rounded`}>
                        {value || 'N/A'}
                      </td>
                    );
                  }
                  
                  return (
                    <td key={columnId} className="px-3 py-3 whitespace-nowrap text-sm text-gray-900">
                      {columnId === 'position' && value !== undefined ? 
                        (value as number).toLocaleString() : 
                        value || 'N/A'
                      }
                </td>
                  );
                })}
              </tr>
            ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    };

export default TickerMetricsTable;
