import React from 'react';
import { GitCompare, Clock, BarChart3 } from 'lucide-react';

const CompareTickersPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <GitCompare className="w-8 h-8 mr-3 text-primary-600" />
                Compare Tickers
              </h1>
              <p className="text-gray-600 mt-2">
                Compare multiple tickers side by side with comprehensive metrics
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center justify-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                <Clock className="w-4 h-4 mr-1" />
                Coming Soon
              </span>
            </div>
          </div>
        </div>

        {/* Coming Soon Content */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12 text-center">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <GitCompare className="w-10 h-10 text-blue-600" />
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Compare Tickers
            </h2>
            
            <p className="text-gray-600 mb-8 leading-relaxed">
              This feature will allow you to compare multiple tickers side by side, 
              analyze their performance metrics, and identify patterns across your portfolio.
            </p>

            {/* Feature Preview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Side-by-Side Comparison</h3>
                <p className="text-sm text-gray-600">
                  Compare key metrics across multiple tickers in a unified view
                </p>
              </div>
              
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <GitCompare className="w-8 h-8 text-green-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Performance Analysis</h3>
                <p className="text-sm text-gray-600">
                  Analyze relative performance and identify top performers
                </p>
              </div>
              
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <Clock className="w-8 h-8 text-purple-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Time Range Comparison</h3>
                <p className="text-sm text-gray-600">
                  Compare tickers across different time periods and date ranges
                </p>
              </div>
            </div>

            {/* Status Message */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-center">
                <Clock className="w-5 h-5 text-blue-600 mr-2" />
                <span className="text-blue-800 font-medium">
                  This feature is currently in development
                </span>
              </div>
              <p className="text-blue-700 text-sm mt-1">
                We're working hard to bring you this powerful comparison tool
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompareTickersPage;
