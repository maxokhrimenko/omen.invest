import React from 'react';
import { TrendingUp, TrendingDown, Shield, AlertTriangle, Target, BarChart3 } from 'lucide-react';
import type { PortfolioMetrics } from '../../hooks/usePortfolioAnalysis';

interface PortfolioMetricsDisplayProps {
  metrics: PortfolioMetrics;
}

const PortfolioMetricsDisplay: React.FC<PortfolioMetricsDisplayProps> = ({ metrics }) => {

  const getTotalReturnColor = (value: string) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue < 10) return 'text-red-600 bg-red-50 border-red-200'; // Bad
    if (numValue > 30) return 'text-green-600 bg-green-50 border-green-200'; // Good
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Caution (10-30%)
  };

  const getAnnualizedReturnColor = (value: string) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue < 5) return 'text-red-600 bg-red-50 border-red-200'; // Bad
    if (numValue > 15) return 'text-green-600 bg-green-50 border-green-200'; // Good
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Caution (5-15%)
  };

  const getVolatilityColor = (value: string) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue > 20) return 'text-red-600 bg-red-50 border-red-200'; // Bad
    if (numValue < 10) return 'text-green-600 bg-green-50 border-green-200'; // Good
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Caution (10-20%)
  };

  const getMaxDrawdownColor = (value: string) => {
    const numValue = Math.abs(parseFloat(value.replace(/[%,$]/g, '')));
    if (numValue > 30) return 'text-red-600 bg-red-50 border-red-200'; // Bad (< -30%)
    if (numValue < 15) return 'text-green-600 bg-green-50 border-green-200'; // Good (> -15%)
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Caution (-30% to -15%)
  };


  const getBetaColor = (value: string) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue > 1.3) return 'text-red-600 bg-red-50 border-red-200'; // High Beta (aggressive)
    if (numValue < 0.7) return 'text-green-600 bg-green-50 border-green-200'; // Low Beta (defensive)
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Market-like Beta
  };

  const getVaRColor = (value: string) => {
    const numValue = Math.abs(parseFloat(value.replace(/[%,$]/g, '')));
    if (numValue > 2.0) return 'text-red-600 bg-red-50 border-red-200'; // High Risk
    if (numValue < 1.0) return 'text-green-600 bg-green-50 border-green-200'; // Low Risk
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Moderate Risk
  };

  const getSharpeColor = (value: string) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue < 0.5) return 'text-red-600 bg-red-50 border-red-200'; // Bad
    if (numValue > 1.5) return 'text-green-600 bg-green-50 border-green-200'; // Good
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Caution (0.5-1.5)
  };

  const getSortinoColor = (value: string) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue < 1.0) return 'text-red-600 bg-red-50 border-red-200'; // Bad
    if (numValue > 2.0) return 'text-green-600 bg-green-50 border-green-200'; // Good
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Caution (1.0-2.0)
  };

  const getCalmarColor = (value: string) => {
    const numValue = parseFloat(value.replace(/[%,$]/g, ''));
    if (numValue < 0.5) return 'text-red-600 bg-red-50 border-red-200'; // Bad
    if (numValue > 1.0) return 'text-green-600 bg-green-50 border-green-200'; // Good
    return 'text-yellow-600 bg-yellow-50 border-yellow-200'; // Caution (0.5-1.0)
  };

  const metricCards = [
    {
      title: 'Total Return',
      value: metrics.totalReturn,
      icon: TrendingUp,
      color: getTotalReturnColor(metrics.totalReturn),
      description: 'Overall portfolio return for the period'
    },
    {
      title: 'Annualized Return',
      value: metrics.annualizedReturn,
      icon: BarChart3,
      color: getAnnualizedReturnColor(metrics.annualizedReturn),
      description: 'Return adjusted for time period'
    },
    {
      title: 'Volatility',
      value: metrics.volatility,
      icon: AlertTriangle,
      color: getVolatilityColor(metrics.volatility),
      description: 'Standard deviation of returns'
    },
    {
      title: 'Sharpe Ratio',
      value: metrics.sharpeRatio,
      icon: Target,
      color: getSharpeColor(metrics.sharpeRatio),
      description: 'Risk-adjusted return measure'
    },
    {
      title: 'Max Drawdown',
      value: metrics.maxDrawdown,
      icon: TrendingDown,
      color: getMaxDrawdownColor(metrics.maxDrawdown),
      description: 'Maximum peak-to-trough decline'
    },
    {
      title: 'Sortino Ratio',
      value: metrics.sortinoRatio,
      icon: Shield,
      color: getSortinoColor(metrics.sortinoRatio),
      description: 'Downside risk-adjusted return'
    },
    {
      title: 'Calmar Ratio',
      value: metrics.calmarRatio,
      icon: Target,
      color: getCalmarColor(metrics.calmarRatio),
      description: 'Return vs max drawdown'
    },
    {
      title: 'VaR (95%)',
      value: metrics.var95,
      icon: AlertTriangle,
      color: getVaRColor(metrics.var95),
      description: 'Value at Risk (95% confidence)'
    },
    {
      title: 'Beta',
      value: metrics.beta,
      icon: BarChart3,
      color: getBetaColor(metrics.beta),
      description: 'Market sensitivity measure'
    }
  ];

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

      {/* Metrics Grid - 3 columns, 3 rows */}
      <div className="grid grid-cols-3 gap-4">
        {metricCards.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div
              key={index}
              className={`p-5 rounded-lg border-2 transition-all duration-200 hover:shadow-md ${metric.color}`}
            >
              <div className="flex items-center mb-4">
                <Icon className="w-6 h-6 mr-3" />
                <h3 className="text-base font-semibold">{metric.title}</h3>
              </div>
              <div className="text-3xl font-bold mb-3">{metric.value}</div>
              <p className="text-sm opacity-80 leading-relaxed">{metric.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PortfolioMetricsDisplay;
