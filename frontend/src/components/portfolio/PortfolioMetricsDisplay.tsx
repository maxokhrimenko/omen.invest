import React, { useRef } from 'react';
import { DollarSign, TrendingUp, AlertTriangle, Coins, Percent } from 'lucide-react';
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
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Portfolio Performance</h2>
      </div>

      {/* Portfolio Performance Metrics - All in one row */}
      <div className="grid grid-cols-5 gap-2 mb-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 flex flex-col items-center justify-center min-h-[60px]">
          <div className="flex items-center gap-1 text-xs font-medium text-blue-700 mb-1">
            <DollarSign className="w-3 h-3" />
            Start Value
          </div>
          <div className="text-sm font-bold text-blue-900">{metrics.startValue}</div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-2 flex flex-col items-center justify-center min-h-[60px]">
          <div className="flex items-center gap-1 text-xs font-medium text-green-700 mb-1">
            <TrendingUp className="w-3 h-3" />
            End Value
          </div>
          <div className="text-sm font-bold text-green-900">{metrics.endValueAnalysis}</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-2 flex flex-col items-center justify-center min-h-[60px]">
          <div className="flex items-center gap-1 text-xs font-medium text-yellow-700 mb-1">
            <AlertTriangle className="w-3 h-3" />
            Missing Data
          </div>
          <div className="text-sm font-bold text-yellow-900">{metrics.endValueMissing}</div>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-2 flex flex-col items-center justify-center min-h-[60px]">
          <div className="flex items-center gap-1 text-xs font-medium text-purple-700 mb-1">
            <Coins className="w-3 h-3" />
            Dividend Yield in $
          </div>
          <div className="text-sm font-bold text-purple-900">{metrics.dividendAmount}</div>
        </div>
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-2 flex flex-col items-center justify-center min-h-[60px]">
          <div className="flex items-center gap-1 text-xs font-medium text-indigo-700 mb-1">
            <Percent className="w-3 h-3" />
            Annual & Total Dividend Yield
          </div>
          <div className="text-xs font-bold text-indigo-900">
            <div>Annual: {metrics.annualizedDividendYield}</div>
            <div>Total: {metrics.totalDividendYield}</div>
          </div>
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
            className="border border-gray-200 rounded-lg flex-1 min-h-[400px] flex flex-col p-4"
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
