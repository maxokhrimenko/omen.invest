import React from 'react';
import { TrendingUp, TrendingDown, Shield, AlertTriangle, Target, BarChart3 } from 'lucide-react';
import type { PortfolioMetrics } from '../../hooks/usePortfolioAnalysis';

interface CompactPortfolioMetricsProps {
  metrics: PortfolioMetrics;
}

const CompactPortfolioMetrics: React.FC<CompactPortfolioMetricsProps> = ({ metrics }) => {
  const getMetricColor = (value: string, thresholds: { good: number; bad: number }) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue >= thresholds.good) return 'text-green-600 bg-green-50 border-green-200';
    if (numValue <= thresholds.bad) return 'text-red-600 bg-red-50 border-red-200';
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  };

  const metricsData = [
    {
      name: 'Total Return',
      value: metrics.totalReturn,
      thresholds: { good: 30, bad: 10 },
      ranges: { green: '≥30%', yellow: '10-30%', red: '<10%' },
      icon: TrendingUp
    },
    {
      name: 'Annualized Return',
      value: metrics.annualizedReturn,
      thresholds: { good: 15, bad: 5 },
      ranges: { green: '≥15%', yellow: '5-15%', red: '<5%' },
      icon: BarChart3
    },
    {
      name: 'Volatility',
      value: metrics.volatility,
      thresholds: { good: 10, bad: 20 },
      ranges: { green: '<10%', yellow: '10-20%', red: '>20%' },
      icon: AlertTriangle
    },
    {
      name: 'Sharpe Ratio',
      value: metrics.sharpeRatio,
      thresholds: { good: 1.5, bad: 0.5 },
      ranges: { green: '≥1.5', yellow: '0.5-1.5', red: '<0.5' },
      icon: Target
    },
    {
      name: 'Max Drawdown',
      value: metrics.maxDrawdown,
      thresholds: { good: -15, bad: -30 },
      ranges: { green: '>-15%', yellow: '-30 to -15%', red: '<-30%' },
      icon: TrendingDown
    },
    {
      name: 'Sortino Ratio',
      value: metrics.sortinoRatio,
      thresholds: { good: 1.5, bad: 0.5 },
      ranges: { green: '≥1.5', yellow: '0.5-1.5', red: '<0.5' },
      icon: Shield
    },
    {
      name: 'Calmar Ratio',
      value: metrics.calmarRatio,
      thresholds: { good: 1.0, bad: 0.3 },
      ranges: { green: '≥1.0', yellow: '0.3-1.0', red: '<0.3' },
      icon: Target
    },
    {
      name: 'VaR (95%)',
      value: metrics.var95,
      thresholds: { good: -2, bad: -5 },
      ranges: { green: '>-2%', yellow: '-5 to -2%', red: '<-5%' },
      icon: AlertTriangle
    },
    {
      name: 'Beta',
      value: metrics.beta,
      thresholds: { good: 0.7, bad: 1.3 },
      ranges: { green: '0.7-1.3', yellow: '<0.7 or >1.3', red: '<0.5 or >1.5' },
      icon: BarChart3
    }
  ];

  return (
    <div className="space-y-2">
      {metricsData.map((metric, index) => {
        const Icon = metric.icon;
        const colorClass = getMetricColor(metric.value, metric.thresholds);
        
        return (
          <div key={index} className={`flex items-center justify-between p-3 rounded-lg border ${colorClass}`}>
            <div className="flex items-center space-x-2">
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{metric.name}</span>
            </div>
            <div className="flex items-center space-x-3">
              {/* Threshold indicators with ranges */}
              <div className="flex items-center space-x-2 text-xs">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 rounded-full bg-green-400"></div>
                  <span className="text-green-700">{metric.ranges.green}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
                  <span className="text-yellow-700">{metric.ranges.yellow}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 rounded-full bg-red-400"></div>
                  <span className="text-red-700">{metric.ranges.red}</span>
                </div>
              </div>
              <span className="text-sm font-bold">{metric.value}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default CompactPortfolioMetrics;
