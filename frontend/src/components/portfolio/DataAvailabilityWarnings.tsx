import React from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, Calendar, TrendingUp } from 'lucide-react';
import type { DataAvailabilityWarnings as DataAvailabilityWarningsType } from '../../hooks/usePortfolioAnalysis';

interface DataAvailabilityWarningsProps {
  warnings: DataAvailabilityWarningsType;
}

const DataAvailabilityWarnings: React.FC<DataAvailabilityWarningsProps> = ({ warnings }) => {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const hasWarnings = warnings.missingTickers.length > 0 || warnings.tickersWithoutStartData.length > 0;
  
  if (!hasWarnings) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5 shadow-sm">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
          </div>
        </div>
        
        <div className="ml-4 flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-amber-900">Data Availability Notice</h3>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleCollapse();
              }}
              className="text-amber-400 hover:text-amber-600 transition-colors p-1 rounded-md hover:bg-amber-100 flex items-center gap-1"
              aria-label={isCollapsed ? "Expand data availability notice" : "Collapse data availability notice"}
              type="button"
            >
              {isCollapsed ? (
                <>
                  <ChevronDown className="w-4 h-4" />
                  <span className="text-xs">Show Details</span>
                </>
              ) : (
                <>
                  <ChevronUp className="w-4 h-4" />
                  <span className="text-xs">Hide Details</span>
                </>
              )}
            </button>
          </div>
          
          {/* Summary when collapsed */}
          {isCollapsed && (
            <div className="mt-3">
              <p className="text-sm text-amber-800">
                {warnings.missingTickers.length > 0 && `${warnings.missingTickers.length} ticker(s) with no data`}
                {warnings.missingTickers.length > 0 && warnings.tickersWithoutStartData.length > 0 && ', '}
                {warnings.tickersWithoutStartData.length > 0 && `${warnings.tickersWithoutStartData.length} ticker(s) with incomplete data`}
              </p>
            </div>
          )}

          {/* Detailed content when expanded */}
          {!isCollapsed && (
            <div className="mt-3 space-y-3">
              {/* Missing Tickers */}
              {warnings.missingTickers.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                    <span className="text-sm font-medium text-red-800">
                      No data available: <span className="font-mono text-red-700">{warnings.missingTickers.join(', ')}</span>
                    </span>
                  </div>
                  <p className="text-xs text-red-600 mt-1 ml-4">These tickers will be excluded from analysis</p>
                </div>
              )}

              {/* Incomplete Data */}
              {warnings.tickersWithoutStartData.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                    <span className="text-sm font-medium text-yellow-800">
                      Incomplete data at start date: <span className="font-mono text-yellow-700">{warnings.tickersWithoutStartData.join(', ')}</span>
                    </span>
                  </div>
                  <p className="text-xs text-yellow-600 mt-1 ml-4">Consider adjusting your start date for complete analysis</p>
                </div>
              )}

              {/* First Available Dates for Problematic Tickers */}
              {Object.keys(warnings.firstAvailableDates).length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center mb-2">
                    <Calendar className="w-4 h-4 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-blue-800">First available data for problematic tickers</span>
                  </div>
                  <p className="text-xs text-blue-600 mb-2">These tickers have data availability issues - their first available dates:</p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {Object.entries(warnings.firstAvailableDates).map(([ticker, date]) => (
                      <div key={ticker} className="flex items-center justify-between bg-white rounded px-2 py-1">
                        <span className="text-xs font-mono text-blue-700 font-medium">{ticker}</span>
                        <span className="text-xs text-blue-600">{new Date(date).toLocaleDateString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendation */}
              <div className="flex items-start bg-white rounded-lg p-3 border border-amber-200">
                <TrendingUp className="w-4 h-4 text-amber-600 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-amber-800">Recommendation</p>
                  <p className="text-xs text-amber-700 mt-1">
                    For more complete analysis, try extending your start date or excluding tickers with limited data.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataAvailabilityWarnings;
