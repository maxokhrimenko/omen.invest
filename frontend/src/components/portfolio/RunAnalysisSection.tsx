import React from 'react';
import DateRangeSelector from './DateRangeSelector';
import AnalysisButton from './AnalysisButton';
import type { DateRange } from './DateRangeSelector';

interface RunAnalysisSectionProps {
  selectedDateRange: DateRange | null;
  onRangeChange: (range: DateRange) => void;
  onAnalyze: (startDate: string, endDate: string) => Promise<void>;
  onClearResults: () => void;
  isLoading: boolean;
  error: string | null;
  hasResults: boolean;
  tickerCount?: number;
}

const RunAnalysisSection: React.FC<RunAnalysisSectionProps> = ({
  selectedDateRange,
  onRangeChange,
  onAnalyze,
  onClearResults,
  isLoading,
  error,
  hasResults,
  tickerCount
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Run Analysis</h2>
      </div>
      
      {/* Three Horizontal Blocks */}
      <div className="flex items-start space-x-6">
        {/* Block 1: Predefined Periods */}
        <div className="flex-1">
          <DateRangeSelector
            selectedRange={selectedDateRange}
            onRangeChange={onRangeChange}
          />
        </div>
        
        {/* Block 2: Analysis Button */}
        <div className="w-48">
          <AnalysisButton
            onAnalyze={onAnalyze}
            onClearResults={onClearResults}
            isLoading={isLoading}
            selectedDateRange={selectedDateRange}
            error={error}
            hasResults={hasResults}
            tickerCount={tickerCount}
          />
        </div>
      </div>
    </div>
  );
};

export default RunAnalysisSection;
