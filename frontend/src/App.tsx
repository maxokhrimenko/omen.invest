import React, { useState, useCallback, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Upload, FileText, BarChart3, Home, CheckCircle, AlertCircle } from 'lucide-react';

// File upload hook
const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileSelect = useCallback((file: File) => {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a CSV file');
      return;
    }
    
    setError(null);
    setUploadedFile(file);
    setSuccess(`File "${file.name}" selected successfully!`);
  }, []);

  const handleUpload = useCallback(async () => {
    if (!uploadedFile) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      // Simulate upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSuccess('Portfolio uploaded successfully!');
    } catch (err) {
      setError('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  }, [uploadedFile]);

  return {
    isUploading,
    uploadedFile,
    error,
    success,
    handleFileSelect,
    handleUpload,
    clearMessages: () => {
      setError(null);
      setSuccess(null);
    }
  };
};

const DashboardPage = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [portfolio, setPortfolio] = useState<any>(() => {
    // Load portfolio from localStorage on component mount
    const saved = localStorage.getItem('portfolio');
    return saved ? JSON.parse(saved) : null;
  });
  const [parseError, setParseError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Show success message when portfolio is loaded from localStorage
  useEffect(() => {
    if (portfolio && !success) {
      setSuccess(`Portfolio loaded: ${portfolio.tickers.length} tickers, ${portfolio.positions.length} positions`);
    }
  }, [portfolio, success]);

  // Update page title based on portfolio state
  useEffect(() => {
    if (portfolio) {
      document.title = `Portfolio Analyzer - ${portfolio.tickers.length} Tickers | ${portfolio.positions.length} Positions`;
    } else {
      document.title = 'Portfolio Analyzer - Professional Investment Analysis';
    }
  }, [portfolio]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setSuccess(`File "${file.name}" selected successfully!`);
      // Process CSV immediately after file selection
      processCSVFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      setUploadedFile(file);
      setSuccess(`File "${file.name}" selected successfully!`);
      // Process CSV immediately after file drop
      processCSVFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleClearPortfolio = () => {
    setPortfolio(null);
    setUploadedFile(null);
    setParseError(null);
    setSuccess(null);
    // Clear portfolio from localStorage
    localStorage.removeItem('portfolio');
  };

  const parseCSV = (csvText: string) => {
    const lines = csvText.split('\n').filter(line => line.trim());
    if (lines.length < 2) {
      throw new Error('CSV file must have at least a header and one data row');
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const tickerIndex = headers.findIndex(h => h === 'ticker');
    const positionIndex = headers.findIndex(h => h === 'position');

    if (tickerIndex === -1 || positionIndex === -1) {
      throw new Error('CSV must contain "ticker" and "position" columns');
    }

    const positions = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      if (values.length >= 2) {
        const ticker = values[tickerIndex];
        const position = parseFloat(values[positionIndex]);
        
        if (ticker && !isNaN(position)) {
          positions.push({ ticker, position });
        }
      }
    }

    if (positions.length === 0) {
      throw new Error('No valid data rows found in CSV');
    }

    const totalPositions = positions.reduce((sum, pos) => sum + pos.position, 0);
    const tickers = [...new Set(positions.map(pos => pos.ticker))];

    return {
      positions,
      totalPositions,
      tickers
    };
  };

  const processCSVFile = (file: File) => {
    setParseError(null);
    setPortfolio(null);
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const csvText = e.target?.result as string;
        const portfolio = parseCSV(csvText);
        setPortfolio(portfolio);
        // Save portfolio to localStorage for persistence
        localStorage.setItem('portfolio', JSON.stringify(portfolio));
        // Show success message
        setSuccess(`Portfolio loaded successfully! ${portfolio.tickers.length} tickers processed.`);
      } catch (error) {
        console.error('CSV parsing error:', error);
        setParseError(error instanceof Error ? error.message : 'Failed to parse CSV file');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Portfolio Management</h1>
          <p className="text-xl text-gray-600">Upload and manage your investment portfolio</p>
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
                <h3 className="text-lg font-semibold text-blue-900 mb-3">CSV Format Requirements</h3>
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
                  {portfolio.positions.reduce((sum: number, pos: any) => sum + pos.position, 0).toLocaleString()}
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
                  {portfolio.positions.length > 0 
                    ? (portfolio.positions.reduce((sum: number, pos: any) => sum + pos.position, 0) / portfolio.positions.length).toFixed(2)
                    : 0
                  }
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-sm font-medium text-gray-500">Position Range</div>
                <div className="text-2xl font-bold text-gray-900">
                  {portfolio.positions.length > 0 
                    ? `${Math.min(...portfolio.positions.map((p: any) => p.position)).toFixed(2)} - ${Math.max(...portfolio.positions.map((p: any) => p.position)).toFixed(0)}`
                    : '0 - 0'
                  }
                </div>
              </div>
            </div>

            {/* Portfolio Table */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Position Details</h3>
                <p className="text-sm text-gray-600 mt-1">Individual ticker positions and weights</p>
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
                      const totalPositions = portfolio.positions.reduce((sum: number, pos: any) => sum + pos.position, 0);
                      const weight = totalPositions > 0 ? (position.position / totalPositions) * 100 : 0;
                      
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


const Sidebar = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="w-72 bg-white border-r border-gray-200 h-screen">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900">Portfolio Analyzer</h1>
        <p className="text-sm text-gray-500 mt-1">Professional Analysis Tool</p>
      </div>
      
      <nav className="p-4 space-y-2">
        <Link
          to="/"
          className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
            isActive('/')
              ? 'bg-blue-50 text-blue-700 border border-blue-200'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Upload className="w-5 h-5 mr-3" />
          <span className="font-medium">Portfolio Management</span>
        </Link>
        
        
        <Link
          to="/portfolio/analysis"
          className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
            isActive('/portfolio/analysis')
              ? 'bg-blue-50 text-blue-700 border border-blue-200'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <BarChart3 className="w-5 h-5 mr-3" />
          <span className="font-medium">Portfolio Analysis</span>
        </Link>
      </nav>
    </div>
  );
};

const MainLayout = () => {
  const location = useLocation();

  // Update page title based on current route
  useEffect(() => {
    switch (location.pathname) {
      case '/':
        document.title = 'Portfolio Analyzer - Portfolio Management';
        break;
      case '/portfolio/analysis':
        document.title = 'Portfolio Analyzer - Analysis Dashboard';
        break;
      default:
        document.title = 'Portfolio Analyzer - Professional Investment Analysis';
    }
  }, [location.pathname]);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/portfolio/analysis" element={<div className="p-8">Portfolio Analysis - Coming Soon</div>} />
        </Routes>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <MainLayout />
    </Router>
  );
}

export default App;