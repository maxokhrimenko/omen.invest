import React, { useState } from 'react';
import { Filter, AlertTriangle } from 'lucide-react';

interface TickerFilterToggleProps {
  showProblematicTickers: boolean;
  onToggle: (show: boolean) => void;
  problematicTickerCount: number;
  totalTickerCount: number;
}

const TickerFilterToggle: React.FC<TickerFilterToggleProps> = ({
  showProblematicTickers,
  onToggle,
  problematicTickerCount,
  totalTickerCount
}) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const cleanTickerCount = totalTickerCount - problematicTickerCount;

  const tooltipText = problematicTickerCount > 0 
    ? `Filter data quality issues. ${problematicTickerCount} ticker(s) have incomplete data. Currently showing ${showProblematicTickers ? 'all' : 'clean'} tickers.`
    : 'All tickers have complete data for the selected period.';

  return (
    <div className="relative">
      {/* Filter Button */}
      <button
        onClick={problematicTickerCount > 0 ? () => onToggle(!showProblematicTickers) : undefined}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        disabled={problematicTickerCount === 0}
        className={`relative flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
          problematicTickerCount === 0
            ? 'bg-gray-100 text-gray-500 border border-gray-200 cursor-not-allowed'
            : showProblematicTickers
            ? 'bg-red-100 text-red-700 border border-red-200 hover:bg-red-200'
            : 'bg-amber-100 text-amber-700 border border-amber-200 hover:bg-amber-200'
        }`}
      >
        <Filter className="w-4 h-4" />
        <span>
          {problematicTickerCount > 0 ? `${cleanTickerCount}/${totalTickerCount}` : 'All Clean'}
        </span>
        {problematicTickerCount > 0 && (
          <AlertTriangle className="w-3 h-3" />
        )}
      </button>

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 z-50">
          <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap shadow-lg">
            {tooltipText}
            <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TickerFilterToggle;
