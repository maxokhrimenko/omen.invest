import React from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, Calendar } from 'lucide-react';
import type { DataWarnings as DataWarningsType } from '../../hooks/usePortfolioAnalysis';

interface DataWarningsProps {
  warnings: DataWarningsType;
}

const DataWarnings: React.FC<DataWarningsProps> = ({ warnings }) => {
  const [showDetails, setShowDetails] = React.useState(false);

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  const hasWarnings = warnings.missingTickers.length > 0 || warnings.tickersWithoutStartData.length > 0;
  
  if (!hasWarnings) {
    return null;
  }

  const totalProblematicTickers = warnings.missingTickers.length + warnings.tickersWithoutStartData.length;
  const allProblematicTickers = [...warnings.missingTickers, ...warnings.tickersWithoutStartData];

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
      <div className="flex items-center justify-between">
        {/* Left side - Warning info */}
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-amber-800">
                Data Notice: {totalProblematicTickers} ticker{totalProblematicTickers !== 1 ? 's' : ''} with data issues
              </span>
              {warnings.missingTickers.length > 0 && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                  {warnings.missingTickers.length} missing
                </span>
              )}
              {warnings.tickersWithoutStartData.length > 0 && (
                <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                  {warnings.tickersWithoutStartData.length} incomplete
                </span>
              )}
            </div>
            <div className="text-xs text-amber-700 mt-1 truncate">
              {allProblematicTickers.slice(0, 5).join(', ')}
              {allProblematicTickers.length > 5 && ` +${allProblematicTickers.length - 5} more`}
            </div>
          </div>
        </div>

        {/* Right side - Action buttons */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <button
            onClick={toggleDetails}
            className="text-xs text-amber-700 hover:text-amber-800 px-2 py-1 rounded hover:bg-amber-100 transition-colors"
          >
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
          <button
            onClick={toggleDetails}
            className="text-amber-400 hover:text-amber-600 transition-colors p-1 rounded hover:bg-amber-100"
            aria-label={showDetails ? "Hide details" : "Show details"}
            type="button"
          >
            {showDetails ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Detailed content when expanded */}
      {showDetails && (
        <div className="mt-3 pt-3 border-t border-amber-200 space-y-3">
          {/* Missing Tickers */}
          {warnings.missingTickers.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-2">
              <div className="flex items-center mb-1">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                <span className="text-xs font-medium text-red-800">No data available</span>
              </div>
              <div className="text-xs text-red-700 font-mono ml-4 break-all">
                {warnings.missingTickers.join(', ')}
              </div>
            </div>
          )}

          {/* Incomplete Data */}
          {warnings.tickersWithoutStartData.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-2">
              <div className="flex items-center mb-1">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                <span className="text-xs font-medium text-yellow-800">Incomplete data at start date</span>
              </div>
              <div className="text-xs text-yellow-700 font-mono ml-4 break-all">
                {warnings.tickersWithoutStartData.join(', ')}
              </div>
            </div>
          )}

          {/* First Available Dates */}
          {Object.keys(warnings.firstAvailableDates).length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
              <div className="flex items-center mb-2">
                <Calendar className="w-3 h-3 text-blue-600 mr-1" />
                <span className="text-xs font-medium text-blue-800">First available dates</span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-1">
                {Object.entries(warnings.firstAvailableDates).map(([ticker, date]) => (
                  <div key={ticker} className="flex items-center justify-between bg-white rounded px-2 py-1 text-xs">
                    <span className="font-mono text-blue-700 font-medium truncate">{ticker}</span>
                    <span className="text-blue-600 ml-1">{new Date(date).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DataWarnings;
