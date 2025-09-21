import React from 'react';
import { Trash2, Download, RefreshCw } from 'lucide-react';
import { Portfolio } from '../../types/portfolio';

interface PortfolioTableProps {
  portfolio: Portfolio;
  onClearPortfolio: () => void;
  onRefreshPortfolio: () => void;
  isRefreshing?: boolean;
}

const PortfolioTable: React.FC<PortfolioTableProps> = ({
  portfolio,
  onClearPortfolio,
  onRefreshPortfolio,
  isRefreshing = false
}) => {
  const handleClearPortfolio = () => {
    if (window.confirm('Are you sure you want to clear the portfolio? This action cannot be undone.')) {
      onClearPortfolio();
    }
  };

  const exportToCSV = () => {
    const csvContent = [
      'ticker,position',
      ...portfolio.positions.map(pos => `${pos.ticker},${pos.position}`)
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'portfolio_export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Portfolio</h2>
          <p className="text-gray-600 mt-1">
            {portfolio.totalPositions} positions • {portfolio.tickers.length} unique tickers
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefreshPortfolio}
            disabled={isRefreshing}
            className="btn btn-secondary btn-sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          
          <button
            onClick={exportToCSV}
            className="btn btn-secondary btn-sm"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </button>
          
          <button
            onClick={handleClearPortfolio}
            className="btn btn-danger btn-sm"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear Portfolio
          </button>
        </div>
      </div>

      {/* Portfolio Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ticker
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Position
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Weight
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {portfolio.positions.map((position, index) => {
                const totalPositions = portfolio.positions.reduce((sum, pos) => sum + pos.position, 0);
                const weight = totalPositions > 0 ? (position.position / totalPositions) * 100 : 0;
                
                return (
                  <tr key={`${position.ticker}-${index}`} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                          <span className="text-xs font-medium text-primary-700">
                            {position.ticker.charAt(0)}
                          </span>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {position.ticker}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {position.position.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {weight.toFixed(2)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Positions</div>
          <div className="text-2xl font-bold text-gray-900">
            {portfolio.positions.reduce((sum, pos) => sum + pos.position, 0).toLocaleString()}
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Unique Tickers</div>
          <div className="text-2xl font-bold text-gray-900">
            {portfolio.tickers.length}
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Average Position</div>
          <div className="text-2xl font-bold text-gray-900">
            {portfolio.totalPositions > 0 
              ? (portfolio.positions.reduce((sum, pos) => sum + pos.position, 0) / portfolio.totalPositions).toFixed(0)
              : 0
            }
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioTable;
