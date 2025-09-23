import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Upload, BarChart3, CheckCircle, AlertCircle, TrendingUp, Settings } from 'lucide-react';
import PortfolioAnalysisPage from './pages/PortfolioAnalysisPage';
import AdministrationPage from './pages/AdministrationPage';
import { apiService } from './services/api';
import Logo from './components/Logo';
import ErrorBoundary from './components/ErrorBoundary';
import { logger } from './utils/logger';
import { ToastProvider } from './contexts/ToastContext';


const DashboardPage = ({ portfolio, setPortfolio }: { portfolio: any, setPortfolio: (portfolio: any) => void }) => {
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
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

  const handleClearPortfolio = async () => {
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
  };


  const processCSVFile = async (file: File) => {
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
  };

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


const Sidebar = ({ portfolio }: { portfolio: any }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const menuItems = [
    {
      path: '/',
      label: 'Portfolio Management',
      icon: Upload,
      badge: null,
      disabled: false
    },
    {
      path: '/portfolio/analysis',
      label: 'Portfolio Analysis',
      icon: BarChart3,
      badge: { text: 'new', color: 'red' },
      disabled: !portfolio
    },
    {
      path: '/tickers/analysis',
      label: 'Tickers Analysis',
      icon: TrendingUp,
      badge: { text: 'soon', color: 'purple' },
      disabled: true
    }
  ];

  const adminItem = {
    path: '/administration',
    label: 'Administration',
    icon: Settings,
    badge: null,
    disabled: false
  };

  const getBadgeClasses = (badge: any) => {
    if (!badge) return '';
    const baseClasses = 'inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium whitespace-nowrap min-w-fit';
    switch (badge.color) {
      case 'red':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'purple':
        return `${baseClasses} bg-purple-100 text-purple-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  return (
    <div className="w-72 bg-white border-r border-gray-200 h-screen flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 flex items-center justify-center">
            <Logo />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900 leading-tight">
              Altidus
            </h1>
            <p className="text-sm text-gray-500 mt-1">Bought the peak,<br />lost it all in a week</p>
            <div className="mt-2">
              <span className="inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 whitespace-nowrap">
                v4.4.4
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <nav className="p-4 space-y-2 flex-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          const isDisabled = item.disabled;
          
          const menuItem = (
            <div
              className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                isDisabled
                  ? 'text-gray-400 cursor-not-allowed opacity-50'
                  : active
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className={`w-5 h-5 mr-3 ${
                isDisabled 
                  ? 'text-gray-400' 
                  : active 
                  ? 'text-blue-600' 
                  : 'text-gray-400'
              }`} />
              <div className="flex-1 flex items-center justify-between min-w-0">
                <span className="font-medium truncate">{item.label}</span>
                {item.badge && (
                  <span className={`${getBadgeClasses(item.badge)} ml-2 flex-shrink-0`}>
                    {item.badge.text}
                  </span>
                )}
              </div>
            </div>
          );
          
          if (isDisabled) {
            return (
              <div key={item.path} onClick={(e) => e.preventDefault()}>
                {menuItem}
              </div>
            );
          }
          
          return (
            <Link key={item.path} to={item.path}>
              {menuItem}
            </Link>
          );
        })}
      </nav>

      {/* Administration link at the bottom */}
      <div className="p-4 border-t border-gray-200">
        {(() => {
          const Icon = adminItem.icon;
          const active = isActive(adminItem.path);
          const isDisabled = adminItem.disabled;
          
          const menuItem = (
            <div
              className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                isDisabled
                  ? 'text-gray-400 cursor-not-allowed opacity-50'
                  : active
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className={`w-5 h-5 mr-3 ${
                isDisabled 
                  ? 'text-gray-400' 
                  : active 
                  ? 'text-blue-600' 
                  : 'text-gray-400'
              }`} />
              <div className="flex-1 flex items-center justify-between min-w-0">
                <span className="font-medium truncate">{adminItem.label}</span>
                {adminItem.badge && (
                  <span className={`${getBadgeClasses(adminItem.badge)} ml-2 flex-shrink-0`}>
                    {adminItem.badge.text}
                  </span>
                )}
              </div>
            </div>
          );
          
          if (isDisabled) {
            return (
              <div onClick={(e) => e.preventDefault()}>
                {menuItem}
              </div>
            );
          }
          
          return (
            <Link to={adminItem.path}>
              {menuItem}
            </Link>
          );
        })()}
      </div>
    </div>
  );
};

const MainLayout = () => {
  const location = useLocation();
  const [portfolio, setPortfolio] = useState<any>(null);

  // Load portfolio from backend on component mount
  useEffect(() => {
    const loadPortfolio = async () => {
      try {
        const portfolioData = await apiService.getPortfolio();
        if (portfolioData) {
          setPortfolio(portfolioData);
        } else {
          setPortfolio(null);
        }
      } catch (error) {
        setPortfolio(null);
      }
    };
    
    loadPortfolio();
  }, []);

  // Refresh portfolio when returning to this page (e.g., after clearing portfolio)
  useEffect(() => {
    const handleFocus = () => {
      const loadPortfolio = async () => {
        try {
          const portfolioData = await apiService.getPortfolio();
          if (portfolioData) {
            setPortfolio(portfolioData);
          } else {
            setPortfolio(null);
          }
        } catch (error) {
          setPortfolio(null);
        }
      };
      loadPortfolio();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  // Update page title based on current route
  useEffect(() => {
    switch (location.pathname) {
      case '/':
        document.title = 'Altidus - Portfolio Management';
        break;
      case '/portfolio/analysis':
        document.title = 'Altidus - Analysis Dashboard';
        break;
      case '/administration':
        document.title = 'Altidus - Administration';
        break;
      default:
        document.title = 'Altidus - Portfolio Analysis';
    }
  }, [location.pathname]);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar portfolio={portfolio} />
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<DashboardPage portfolio={portfolio} setPortfolio={setPortfolio} />} />
          <Route path="/portfolio/analysis" element={<PortfolioAnalysisPage />} />
          <Route path="/administration" element={<AdministrationPage />} />
        </Routes>
      </div>
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <Router>
          <MainLayout />
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;