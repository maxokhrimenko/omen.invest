import React from 'react';
import { Play, Loader2, AlertCircle, Clock } from 'lucide-react';
import type { DateRange } from './DateRangeSelector';
import { calculateAnalysisTimeout, formatTimeout } from '../../utils/timeoutCalculator';

interface AnalysisTriggerProps {
  onAnalyze: (startDate: string, endDate: string) => Promise<void>;
  onClearResults: () => void;
  isLoading: boolean;
  selectedDateRange: DateRange | null;
  error: string | null;
  hasResults: boolean;
  tickerCount?: number;
}

const AnalysisTrigger: React.FC<AnalysisTriggerProps> = ({
  onAnalyze,
  onClearResults,
  isLoading,
  selectedDateRange,
  error,
  hasResults,
  tickerCount
}) => {
  const handleAnalyze = async () => {
    if (selectedDateRange) {
      await onAnalyze(selectedDateRange.startDate, selectedDateRange.endDate);
    }
  };

  const isDisabled = !selectedDateRange || isLoading;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Calculate estimated timeout
  const estimatedTimeout = selectedDateRange && tickerCount 
    ? calculateAnalysisTimeout(tickerCount, selectedDateRange.startDate, selectedDateRange.endDate)
    : null;

  return (
    <div className="flex flex-col items-center space-y-3">
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 w-full">
          <div className="flex items-center">
            <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
            <div>
              <div className="text-sm font-medium text-red-900">Analysis Failed</div>
              <div className="text-xs text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Timeout Estimate */}
      {estimatedTimeout && !isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 w-full">
          <div className="flex items-center">
            <Clock className="w-4 h-4 text-blue-600 mr-2" />
            <div>
              <div className="text-sm font-medium text-blue-900">Estimated Time</div>
              <div className="text-xs text-blue-700">
                {formatTimeout(estimatedTimeout)} for {tickerCount} tickers
              </div>
            </div>
          </div>
        </div>
      )}

              {/* Analysis Button */}
              <div className="w-full">
                <button
                  onClick={handleAnalyze}
                  disabled={isDisabled}
                  className={`w-full inline-flex items-center justify-center px-6 py-3 text-base font-semibold rounded-lg transition-all duration-200 ${
                    isDisabled
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg transform hover:-translate-y-0.5'
                  }`}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      Start Analysis
                    </>
                  )}
                </button>
              </div>

              {/* Clear Results Button */}
              <div className="w-full">
                <button
                  onClick={onClearResults}
                  disabled={!hasResults || isLoading}
                  className={`w-full inline-flex items-center justify-center px-6 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                    !hasResults || isLoading
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 hover:border-red-300'
                  }`}
                >
                  Clear Results
                </button>
              </div>

              {/* Selected Range Display */}
              {selectedDateRange && (
                <div className="w-full mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="text-xs font-medium text-blue-900 mb-1">Selected Range</div>
                  <div className="text-xs text-blue-700">
                    {formatDate(selectedDateRange.startDate)} - {formatDate(selectedDateRange.endDate)}
                  </div>
                </div>
              )}

              {/* Status Messages */}
              {!selectedDateRange && !isLoading && (
                <div className="text-center mt-3">
                  <div className="inline-flex items-center px-3 py-1 bg-yellow-50 text-yellow-700 rounded-lg">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">
                      Please select a date range
                    </span>
                  </div>
                </div>
              )}
    </div>
  );
};

export default AnalysisTrigger;
