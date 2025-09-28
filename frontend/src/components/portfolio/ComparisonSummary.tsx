import React from 'react';
import { Trophy, TrendingDown, BarChart3, Shield } from 'lucide-react';
import type { TickerComparisonData } from '../../types/portfolio';

interface ComparisonSummaryProps {
  bestPerformers: TickerComparisonData[];
  worstPerformers: TickerComparisonData[];
  bestSharpe: TickerComparisonData[];
  lowestRisk: TickerComparisonData[];
}

const ComparisonSummary: React.FC<ComparisonSummaryProps> = ({
  bestPerformers = [],
  worstPerformers = [],
  bestSharpe = [],
  lowestRisk = []
}) => {
  const categories = [
    {
      title: 'Top Performers',
      data: bestPerformers,
      icon: Trophy,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      iconColor: 'text-green-600',
      textColor: 'text-green-900',
      metricColor: 'text-green-700',
      metricLabel: 'Annual Return'
    },
    {
      title: 'Worst Performers',
      data: worstPerformers,
      icon: TrendingDown,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      iconColor: 'text-red-600',
      textColor: 'text-red-900',
      metricColor: 'text-red-700',
      metricLabel: 'Annual Return'
    },
    {
      title: 'Best Sharpe Ratio',
      data: bestSharpe,
      icon: BarChart3,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      iconColor: 'text-blue-600',
      textColor: 'text-blue-900',
      metricColor: 'text-blue-700',
      metricLabel: 'Sharpe Ratio'
    },
    {
      title: 'Lowest Risk',
      data: lowestRisk,
      icon: Shield,
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      iconColor: 'text-purple-600',
      textColor: 'text-purple-900',
      metricColor: 'text-purple-700',
      metricLabel: 'Volatility'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-6">
      {categories.map((category, categoryIndex) => {
        const Icon = category.icon;
        return (
          <div
            key={categoryIndex}
            className={`${category.bgColor} ${category.borderColor} border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Icon className={`w-5 h-5 ${category.iconColor}`} />
                <h3 className={`text-sm font-medium ${category.textColor}`}>
                  {category.title}
                </h3>
              </div>
            </div>
            
            <div className="space-y-3">
              {category.data && category.data.length > 0 ? (
                category.data.map((ticker, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        index === 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {index + 1}
                      </div>
                      <span className={`text-sm font-semibold ${category.textColor}`}>
                        {ticker.ticker}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className={`text-sm font-bold ${category.textColor}`}>
                        {category.title === 'Best Sharpe Ratio' ? ticker.sharpeRatio : 
                         category.title === 'Lowest Risk' ? ticker.volatility :
                         ticker.annualizedReturn}
                      </div>
                      <div className="text-xs text-gray-500">
                        {category.metricLabel}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4">
                  <div className="text-sm text-gray-500">No data available</div>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ComparisonSummary;
