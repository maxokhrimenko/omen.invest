import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Upload, 
  BarChart3, 
  TrendingUp, 
  FileText,
  ArrowRight,
} from 'lucide-react';

const DashboardPage: React.FC = () => {
  const features = [
    {
      icon: Upload,
      title: 'Portfolio Upload',
      description: 'Upload your portfolio CSV file and manage your positions',
      link: '/portfolio/upload',
      color: 'bg-blue-500'
    },
    {
      icon: BarChart3,
      title: 'Portfolio Analysis',
      description: 'Get analysis of your portfolio performance',
      link: '/portfolio/analysis',
      color: 'bg-green-500'
    },
    {
      icon: TrendingUp,
      title: 'Ticker Analysis',
      description: 'Analyze individual tickers in your portfolio',
      link: '/tickers/analysis',
      color: 'bg-purple-500'
    }
  ];

  const stats = [
    {
      label: 'Total Positions',
      value: '0',
      icon: FileText,
      color: 'text-blue-600'
    },
    {
      label: 'Unique Tickers',
      value: '0',
      icon: TrendingUp,
      color: 'text-green-600'
    },
    {
      label: 'Last Analysis',
      value: 'Never',
      icon: BarChart3,
      color: 'text-purple-600'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Omen Screen
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upload your portfolio and get analysis with metrics, 
          performance insights, and risk assessment.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg bg-gray-50`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Features Grid */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Get Started</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Link
                key={index}
                to={feature.link}
                className="group bg-white p-6 rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-lg transition-all duration-200"
              >
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg ${feature.color} text-white`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 mt-2">{feature.description}</p>
                    <div className="flex items-center text-primary-600 text-sm font-medium mt-4 group-hover:text-primary-700">
                      Get started
                      <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Getting Started Steps */}
      <div className="bg-gray-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">How to Get Started</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
              1
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Portfolio</h3>
            <p className="text-gray-600">
              Upload your portfolio CSV file with ticker symbols and position amounts
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
              2
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyze Performance</h3>
            <p className="text-gray-600">
              Get analysis including returns, risk metrics, and comparisons
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
              3
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Make Decisions</h3>
            <p className="text-gray-600">
              Use insights to make informed investment decisions and optimize your portfolio
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
