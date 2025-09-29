import React from 'react';
import {
  Scale,
  Gauge,
  Clock,
  Percent,
  Link,
  GitPullRequest,
  TrendingUp,
  TrendingDown,
  Shield
} from 'lucide-react';
import type { TickerComparisonData } from '../../types/portfolio';
import { getMetricColorClasses, parseMetricValue } from '../../utils/tickerColorCoding';

interface AdvancedMetricsCardsProps {
  bestCalmar: TickerComparisonData[];
  worstCalmar: TickerComparisonData[];
  bestSortino: TickerComparisonData[];
  worstSortino: TickerComparisonData[];
  bestMaxDrawdown: TickerComparisonData[];
  worstMaxDrawdown: TickerComparisonData[];
  bestUlcer: TickerComparisonData[];
  worstUlcer: TickerComparisonData[];
  bestTimeUnderWater: TickerComparisonData[];
  worstTimeUnderWater: TickerComparisonData[];
  bestCvar: TickerComparisonData[];
  worstCvar: TickerComparisonData[];
  bestCorrelation: TickerComparisonData[];
  worstCorrelation: TickerComparisonData[];
  bestRiskContribution: TickerComparisonData[];
  worstRiskContribution: TickerComparisonData[];
  // Traditional metrics moved to advanced section
  bestSharpe: TickerComparisonData[];
  worstSharpe: TickerComparisonData[];
  bestRisk: TickerComparisonData[];
  worstRisk: TickerComparisonData[];
}

interface MetricCardProps {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  bestData: TickerComparisonData[];
  worstData: TickerComparisonData[];
  metricKey: keyof TickerComparisonData;
  formatValue?: (value: string) => string;
  metricName: string; // For color coding
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  description,
  icon: Icon,
  bestData,
  worstData,
  metricKey,
  formatValue = (value) => value,
  metricName
}) => {
  const getValue = (item: TickerComparisonData) => {
    const value = item[metricKey];
    return formatValue(value);
  };

  const getColorClasses = (value: string) => {
    const numValue = parseMetricValue(value);
    if (numValue === null) return 'text-gray-400';
    return getMetricColorClasses(metricName, numValue);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
      {/* Card Header */}
      <div className="flex items-start mb-6">
        <Icon className="w-6 h-6 text-primary-600 mr-3 flex-shrink-0 mt-0.5" />
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
          <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
        </div>
      </div>
      
      {/* Top 5 and Worst 5 in side-by-side layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 5 Section */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-green-700 mb-3 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" />
            Top 5
          </h4>
          <div className="space-y-2">
            {bestData.length > 0 ? (
              bestData.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-yellow-100 text-yellow-800">
                      {index + 1}
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{item.ticker}</span>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-bold ${getColorClasses(getValue(item)).split(' ')[0]}`}>
                      {getValue(item)}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-gray-500 py-4 text-center">No data available</div>
            )}
          </div>
        </div>

        {/* Worst 5 Section */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-red-700 mb-3 flex items-center">
            <TrendingDown className="w-4 h-4 mr-2" />
            Worst 5
          </h4>
          <div className="space-y-2">
            {worstData.length > 0 ? (
              worstData.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-gray-100 text-gray-600">
                      {index + 1}
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{item.ticker}</span>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-bold ${getColorClasses(getValue(item)).split(' ')[0]}`}>
                      {getValue(item)}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-gray-500 py-4 text-center">No data available</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const AdvancedMetricsCards: React.FC<AdvancedMetricsCardsProps> = ({
  bestCalmar, worstCalmar,
  bestSortino, worstSortino,
  bestMaxDrawdown, worstMaxDrawdown,
  bestUlcer, worstUlcer,
  bestTimeUnderWater, worstTimeUnderWater,
  bestCvar, worstCvar,
  bestCorrelation, worstCorrelation,
  bestRiskContribution, worstRiskContribution,
  bestRisk, worstRisk,
}) => {
  const metrics = [
    {
      title: 'Risk (Volatility)',
      description: 'Price volatility measure, lower is better.',
      icon: Shield,
      bestData: bestRisk,
      worstData: worstRisk,
      metricKey: 'volatility' as keyof TickerComparisonData,
      formatValue: (value: string) => value,
      metricName: 'volatility'
    },
    {
      title: 'Calmar Ratio',
      description: 'Return to max drawdown ratio, higher is better.',
      icon: Scale,
      bestData: bestCalmar,
      worstData: worstCalmar,
      metricKey: 'calmarRatio' as keyof TickerComparisonData,
      formatValue: (value: string) => parseFloat(value).toFixed(2),
      metricName: 'calmarRatio'
    },
    {
      title: 'Sortino Ratio',
      description: 'Downside risk-adjusted return, higher is better.',
      icon: TrendingUp,
      bestData: bestSortino,
      worstData: worstSortino,
      metricKey: 'sortinoRatio' as keyof TickerComparisonData,
      formatValue: (value: string) => parseFloat(value).toFixed(2),
      metricName: 'sortinoRatio'
    },
    {
      title: 'Max Drawdown',
      description: 'Maximum peak-to-trough decline, less negative is better.',
      icon: TrendingDown,
      bestData: bestMaxDrawdown,
      worstData: worstMaxDrawdown,
      metricKey: 'maxDrawdown' as keyof TickerComparisonData,
      formatValue: (value: string) => value,
      metricName: 'maxDrawdown'
    },
    {
      title: 'Ulcer Index',
      description: 'Measures drawdown depth and duration, lower is better.',
      icon: Gauge,
      bestData: bestUlcer,
      worstData: worstUlcer,
      metricKey: 'ulcerIndex' as keyof TickerComparisonData,
      formatValue: (value: string) => parseFloat(value).toFixed(4),
      metricName: 'ulcerIndex'
    },
    {
      title: 'Time Under Water',
      description: 'Fraction of time spent below previous peak, lower is better.',
      icon: Clock,
      bestData: bestTimeUnderWater,
      worstData: worstTimeUnderWater,
      metricKey: 'timeUnderWater' as keyof TickerComparisonData,
      formatValue: (value: string) => `${(parseFloat(value) * 100).toFixed(2)}%`,
      metricName: 'timeUnderWater'
    },
    {
      title: 'CVaR 95%',
      description: 'Expected shortfall at 95% confidence, lower (more negative) is better.',
      icon: Percent,
      bestData: bestCvar,
      worstData: worstCvar,
      metricKey: 'cvar95' as keyof TickerComparisonData,
      formatValue: (value: string) => `${parseFloat(value).toFixed(2)}%`,
      metricName: 'cvar95'
    },
    {
      title: 'Correlation to Portfolio',
      description: 'Measures how ticker moves with the portfolio, lower absolute value is better for diversification.',
      icon: Link,
      bestData: bestCorrelation,
      worstData: worstCorrelation,
      metricKey: 'correlationToPortfolio' as keyof TickerComparisonData,
      formatValue: (value: string) => parseFloat(value).toFixed(2),
      metricName: 'correlationToPortfolio'
    },
    {
      title: 'Risk Contribution',
      description: 'Percentage of portfolio variance contributed by the ticker, lower is better.',
      icon: GitPullRequest,
      bestData: bestRiskContribution,
      worstData: worstRiskContribution,
      metricKey: 'riskContributionPercent' as keyof TickerComparisonData,
      formatValue: (value: string) => `${parseFloat(value).toFixed(2)}%`,
      metricName: 'riskContributionPercent'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header - Left aligned like TickerAnalysisPage */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-900">Advanced Metrics Analysis</h2>
        <p className="text-gray-600 mt-2">Top 5 best and worst performers for each advanced metric</p>
      </div>
      
      {/* Grid with 3 cards per row */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {metrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            description={metric.description}
            icon={metric.icon}
            bestData={metric.bestData}
            worstData={metric.worstData}
            metricKey={metric.metricKey}
            formatValue={metric.formatValue}
            metricName={metric.metricName}
          />
        ))}
      </div>
    </div>
  );
};

export default AdvancedMetricsCards;