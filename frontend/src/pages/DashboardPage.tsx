import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';

interface DashboardPageProps {
  portfolio: any;
  setPortfolio: (portfolio: any) => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ portfolio, setPortfolio }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Show success message when portfolio is loaded
  useEffect(() => {
    if (portfolio && !success) {
      setSuccess(`Portfolio loaded: ${portfolio.tickers.length} tickers, ${portfolio.positions.length} positions`);
    }
  }, [portfolio, success]);

  // Update page title based on portfolio state
  useEffect(() => {
    if (portfolio) {
      document.title = `Altidus - ${portfolio.tickers.length} Tickers | ${portfolio.positions.length} Positions`;
    } else {
      document.title = 'Altidus - Deep Portfolio Analysis';
    }
  }, [portfolio]);

  // Memoize expensive calculations
  const portfolioStats = useMemo(() => {
    if (!portfolio) return null;
    
    const totalPositions = portfolio.positions.reduce((sum: number, pos: any) => sum + pos.position, 0);
    const averagePosition = portfolio.positions.length > 0 
      ? totalPositions / portfolio.positions.length 
      : 0;
    const minPosition = portfolio.positions.length > 0 
      ? Math.min(...portfolio.positions.map((p: any) => p.position))
      : 0;
    const maxPosition = portfolio.positions.length > 0 
      ? Math.max(...portfolio.positions.map((p: any) => p.position))
      : 0;
    
    return {
      totalPositions,
      averagePosition,
      minPosition,
      maxPosition
    };
  }, [portfolio]);

  const processCSVFile = useCallback(async (file: File) => {
    setParseError(null);
    setPortfolio(null);
    
    try {
      const response = await apiService.uploadPortfolio(file);
      
      if (response.success && response.portfolio) {
        setPortfolio(response.portfolio);
        setSuccess(`Portfolio loaded successfully! ${response.portfolio.tickers.length} tickers processed.`);
        
        // Clear any existing analysis results since we have a new portfolio
        localStorage.removeItem('portfolioAnalysisResults');
        localStorage.removeItem('portfolioAnalysisDateRange');
      } else {
        setParseError(response.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Portfolio upload error:', error);
      setParseError(error instanceof Error ? error.message : 'Failed to upload portfolio');
    }
  }, []);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      logger.logUserAction('file_selected', { 
        fileName: file.name, 
        fileSize: file.size, 
        fileType: file.type 
      });
      setUploadedFile(file);
      setSuccess(`File "${file.name}" selected successfully!`);
      // Process CSV immediately after file selection
      processCSVFile(file);
    }
  }, [processCSVFile]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      setUploadedFile(file);
      setSuccess(`File "${file.name}" selected successfully!`);
      // Process CSV immediately after file drop
      processCSVFile(file);
    }
  }, [processCSVFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleClearPortfolio = useCallback(async () => {
    try {
      await apiService.clearPortfolio();
      setPortfolio(null);
      setUploadedFile(null);
      setParseError(null);
      setSuccess('Portfolio cleared successfully!');
      
      // Clear portfolio from localStorage
      localStorage.removeItem('portfolio');
      
      // Clear any existing analysis results
      localStorage.removeItem('portfolioAnalysisResults');
      localStorage.removeItem('portfolioAnalysisDateRange');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      console.error('Failed to clear portfolio:', error);
      setParseError('Failed to clear portfolio');
    }
  }, [setPortfolio]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Portfolio Management</h1>
          <p className="text-xl text-gray-600">Upload and manage your portfolio</p>
        </div>

        {/* Status Messages */}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
              <p className="text-green-800 font-medium">{success}</p>
            </div>
          </div>
        )}

        {parseError && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <p className="text-red-800 font-medium">CSV Error: {parseError}</p>
            </div>
          </div>
        )}

        {!portfolio ? (
          /* Upload Section */
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Upload Portfolio CSV</h2>
              
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-400 transition-colors cursor-pointer"
              >
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>
                
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {uploadedFile ? 'File Selected' : 'Drag & Drop Your CSV File'}
                </h3>
                
                <p className="text-gray-600 mb-6">
                  {uploadedFile 
                    ? `Selected: ${uploadedFile.name}` 
                    : 'or click to browse your computer'
                  }
                </p>
                
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                
                <label
                  htmlFor="file-upload"
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors cursor-pointer"
                >
                  <Upload className="w-5 h-5 mr-2" />
                  Choose File
                </label>
              </div>

              {/* CSV Format Info */}
              <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-3">CSV Format</h3>
                <div className="text-sm text-blue-800 space-y-2">
                  <p>• First row should contain headers: <code className="bg-blue-100 px-2 py-1 rounded">ticker,position</code></p>
                  <p>• Each row should contain a ticker symbol and position amount</p>
                  <p>• Example format:</p>
                  <div className="bg-blue-100 p-3 rounded font-mono text-xs">
                    <div>ticker,position</div>
                    <div>AAPL,10</div>
                    <div>GOOGL,5</div>
                    <div>MSFT,8</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Portfolio Display Section */
          <div className="space-y-6">
            {/* Portfolio Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">Portfolio</h2>
                <p className="text-gray-600 mt-1">
                  {portfolio.totalPositions} positions • {portfolio.tickers.length} unique tickers
                </p>
              </div>
              
              <button
                onClick={handleClearPortfolio}
                className="inline-flex items-center px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
              >
                <AlertCircle className="w-4 h-4 mr-2" />
                Clear Portfolio
              </button>
            </div>

            {/* Portfolio Summary - Moved to top for better UX */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-sm font-medium text-gray-500">Total Positions</div>
                <div className="text-2xl font-bold text-gray-900">
                  {portfolioStats?.totalPositions.toLocaleString() || 0}
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-sm font-medium text-gray-500">Unique Tickers</div>
                <div className="text-2xl font-bold text-gray-900">
                  {portfolio.tickers.length}
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-sm font-medium text-gray-500">Average Position</div>
                <div className="text-2xl font-bold text-gray-900">
                  {portfolioStats?.averagePosition.toFixed(2) || 0}
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-sm font-medium text-gray-500">Position Range</div>
                <div className="text-2xl font-bold text-gray-900">
                  {portfolioStats ? `${portfolioStats.minPosition.toFixed(2)} - ${portfolioStats.maxPosition.toFixed(0)}` : '0 - 0'}
                </div>
              </div>
            </div>

            {/* Portfolio Table */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Position Details</h3>
                <p className="text-sm text-gray-600 mt-1">Ticker positions and weights</p>
              </div>
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
                    {portfolio.positions.map((position: any, index: number) => {
                      const weight = portfolioStats?.totalPositions ? (position.position / portfolioStats.totalPositions) * 100 : 0;
                      
                      return (
                        <tr key={`${position.ticker}-${index}`} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {index + 1}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                                <span className="text-xs font-medium text-blue-700">
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
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
