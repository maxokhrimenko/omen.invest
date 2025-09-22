import React, { useRef } from 'react';
import PortfolioMetricsCompact from './PortfolioMetricsCompact';
import PortfolioChart from './PortfolioChart';
import type { PortfolioMetrics } from '../../hooks/usePortfolioAnalysis';

interface PortfolioMetricsDisplayProps {
  metrics: PortfolioMetrics;
  timeSeriesData: {
    portfolioValues: Record<string, number>;
    sp500Values: Record<string, number>;
    nasdaqValues: Record<string, number>;
  };
}

const PortfolioMetricsDisplay: React.FC<PortfolioMetricsDisplayProps> = ({ 
  metrics, 
  timeSeriesData 
}) => {
  const metricsRef = useRef<HTMLDivElement>(null);

  const parsedStartValue = parseFloat(metrics.startValue.replace(/[$,]/g, ''));

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Portfolio Performance</h2>
        <div className="text-sm text-gray-500">
          {metrics.startValue} → {metrics.endValue}
        </div>
      </div>

      {/* Portfolio Value Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <div className="text-sm font-medium text-blue-700 mb-1">Start Value</div>
          <div className="text-lg font-bold text-blue-900">{metrics.startValue}</div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <div className="text-sm font-medium text-green-700 mb-1">End Value</div>
          <div className="text-lg font-bold text-green-900">{metrics.endValueAnalysis}</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
          <div className="text-sm font-medium text-yellow-700 mb-1">Missing Data</div>
          <div className="text-lg font-bold text-yellow-900">{metrics.endValueMissing}</div>
        </div>
      </div>

      {/* Main Content: 40% Metrics + 60% Chart */}
      <div className="flex gap-6">
        {/* Left side: Compact Metrics (40%) */}
        <div className="w-2/5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          <div ref={metricsRef}>
            <PortfolioMetricsCompact metrics={metrics} />
          </div>
        </div>

        {/* Right side: Chart (60%) */}
        <div className="w-3/5 flex flex-col">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Comparison</h3>
          <div 
            className="border border-gray-200 rounded-lg flex-1 min-h-[400px] flex flex-col"
          >
            <PortfolioChart
              portfolioValues={timeSeriesData.portfolioValues}
              sp500Values={timeSeriesData.sp500Values}
              nasdaqValues={timeSeriesData.nasdaqValues}
              startValue={parsedStartValue}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioMetricsDisplay;
