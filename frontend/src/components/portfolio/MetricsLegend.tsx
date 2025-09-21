import React from 'react';
import { TrendingUp, TrendingDown, Shield, Target, AlertTriangle, BarChart3, Calculator, Info } from 'lucide-react';

const MetricsLegend: React.FC = () => {
  const portfolioMetrics = [
    {
      name: 'Total Return',
      description: 'Overall portfolio return for the analysis period',
      formula: '(End Value / Start Value) - 1',
      thresholds: [
        { range: '< 10%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '10% - 30%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> 30%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: TrendingUp
    },
    {
      name: 'Annualized Return',
      description: 'Return adjusted for time period',
      formula: '(1 + Total Return)^(252/days) - 1',
      thresholds: [
        { range: '< 5%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '5% - 15%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> 15%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: BarChart3
    },
    {
      name: 'Volatility',
      description: 'Standard deviation of daily returns',
      formula: 'std_daily_return × √252',
      thresholds: [
        { range: '> 20%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '10% - 20%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '< 10%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: AlertTriangle
    },
    {
      name: 'Sharpe Ratio',
      description: 'Risk-adjusted return measure',
      formula: '√252 × (mean - rf) / std',
      thresholds: [
        { range: '< 0.5', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '0.5 - 1.5', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> 1.5', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: Target
    },
    {
      name: 'Max Drawdown',
      description: 'Maximum peak-to-trough decline',
      formula: 'min((current - max) / max)',
      thresholds: [
        { range: '< -30%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '-30% to -15%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> -15%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: TrendingDown
    },
    {
      name: 'Sortino Ratio',
      description: 'Downside risk-adjusted return',
      formula: '√252 × (mean - rf) / std_downside',
      thresholds: [
        { range: '< 1.0', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '1.0 - 2.0', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> 2.0', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: Shield
    },
    {
      name: 'Calmar Ratio',
      description: 'Return vs maximum drawdown',
      formula: 'Annualized Return / |Max Drawdown|',
      thresholds: [
        { range: '< 0.5', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '0.5 - 1.0', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> 1.0', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: Target
    },
    {
      name: 'VaR (95%)',
      description: 'Value at Risk - max expected loss',
      formula: '-(1.645 × std - mean) × 100',
      thresholds: [
        { range: '> 2.0%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '1.0% - 2.0%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '< 1.0%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: AlertTriangle
    },
    {
      name: 'Beta',
      description: 'Market sensitivity vs S&P 500',
      formula: 'cov(portfolio, benchmark) / var(benchmark)',
      thresholds: [
        { range: '> 1.3', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '0.7 - 1.3', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '< 0.7', color: 'bg-green-100 text-green-800', level: 'Good' }
      ],
      icon: BarChart3
    }
  ];

  const tickerMetrics = [
    {
      name: 'Annualized Return',
      description: 'Individual ticker return',
      thresholds: [
        { range: '< 5%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '5% - 20%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> 20%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ]
    },
    {
      name: 'Volatility',
      description: 'Individual ticker volatility',
      thresholds: [
        { range: '> 50%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '30% - 50%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '< 30%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ]
    },
    {
      name: 'Max Drawdown',
      description: 'Individual ticker max drawdown',
      thresholds: [
        { range: '< -50%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '-50% to -30%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> -30%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ]
    },
    {
      name: 'Dividend Yield',
      description: 'Annualized dividend yield',
      thresholds: [
        { range: '< 1%', color: 'bg-red-100 text-red-800', level: 'Bad' },
        { range: '1% - 4%', color: 'bg-yellow-100 text-yellow-800', level: 'Caution' },
        { range: '> 4%', color: 'bg-green-100 text-green-800', level: 'Good' }
      ]
    }
  ];

  const dividendFrequencies = [
    { frequency: 'Monthly', icon: '🟢', description: 'Monthly payments' },
    { frequency: 'Quarterly', icon: '🔵', description: 'Quarterly payments' },
    { frequency: 'Semi-Annual', icon: '🟡', description: 'Twice yearly' },
    { frequency: 'Annual', icon: '🟠', description: 'Once yearly' },
    { frequency: 'Irregular', icon: '🔴', description: 'Inconsistent' }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Description */}
      <div className="text-center mb-6">
        <p className="text-gray-600">Understanding portfolio performance metrics and their interpretations</p>
      </div>

      {/* Portfolio Metrics Grid */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
          Portfolio Metrics
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {portfolioMetrics.map((metric, index) => {
            const Icon = metric.icon;
            return (
              <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start mb-3">
                  <Icon className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-gray-900 text-sm">{metric.name}</h4>
                    <p className="text-xs text-gray-600 mt-1">{metric.description}</p>
                  </div>
                </div>
                
                <div className="mb-3">
                  <div className="flex items-center text-xs text-gray-500 mb-1">
                    <Calculator className="w-3 h-3 mr-1" />
                    Formula
                  </div>
                  <code className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded block font-mono">
                    {metric.formula}
                  </code>
                </div>

                <div className="space-y-1">
                  {metric.thresholds.map((threshold, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${threshold.color}`}>
                        {threshold.range}
                      </span>
                      <span className="text-gray-600 font-medium">{threshold.level}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Ticker Metrics Grid */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2 text-green-600" />
          Ticker Metrics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {tickerMetrics.map((metric, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <h4 className="font-semibold text-gray-900 text-sm mb-2">{metric.name}</h4>
              <p className="text-xs text-gray-600 mb-3">{metric.description}</p>
              <div className="space-y-1">
                {metric.thresholds.map((threshold, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${threshold.color}`}>
                      {threshold.range}
                    </span>
                    <span className="text-gray-600 font-medium">{threshold.level}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dividend Frequencies */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Shield className="w-5 h-5 mr-2 text-purple-600" />
          Dividend Frequencies
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {dividendFrequencies.map((freq, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-3 text-center hover:shadow-md transition-shadow">
              <div className="text-2xl mb-2">{freq.icon}</div>
              <div className="font-medium text-gray-900 text-sm">{freq.frequency}</div>
              <p className="text-xs text-gray-600 mt-1">{freq.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Important Notes */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Info className="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">Important Notes</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-blue-800">
              <div>• Thresholds based on developed-market equities</div>
              <div>• Different asset classes need adjusted thresholds</div>
              <div>• Longer periods provide more reliable metrics</div>
              <div>• High dividend yields (&gt;8%) may signal distress</div>
              <div>• Beta &lt; 0.7 indicates defensive position</div>
              <div>• All calculations use 252 trading days per year</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsLegend;
