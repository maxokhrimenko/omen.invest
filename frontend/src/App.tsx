import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Upload, BarChart3, TrendingUp, Settings, GitCompare } from 'lucide-react';
import DashboardPage from './pages/DashboardPage';
import PortfolioAnalysisPage from './pages/PortfolioAnalysisPage';
import TickerAnalysisPage from './pages/TickerAnalysisPage';
import CompareTickersPage from './pages/CompareTickersPage';
import AdministrationPage from './pages/AdministrationPage';
import { apiService } from './services/api';
import Logo from './components/Logo';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './contexts/ToastContext';




const Sidebar = ({ portfolio }: { portfolio: any }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const menuGroups = [
    {
      title: 'PORTFOLIO',
      items: [
        {
          path: '/',
          label: 'Portfolio Management',
          icon: Upload,
          badge: null,
          disabled: false
        }
      ]
    },
    {
      title: 'ANALYSIS',
      items: [
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
          badge: { text: 'new', color: 'red' },
          disabled: !portfolio
        },
        {
          path: '/tickers/compare',
          label: 'Compare Tickers',
          icon: GitCompare,
          badge: { text: 'coming soon', color: 'purple' },
          disabled: true
        }
      ]
    }
  ];

  const adminItem = {
    path: '/administration',
    label: 'Administration',
    icon: Settings,
    badge: undefined as { text: string; color: string } | undefined,
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
            <p className="text-sm text-gray-500 mt-1">Charts rise,<br />charts may fall</p>
            <div className="mt-2">
              <span className="inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 whitespace-nowrap">
                v4.4.9
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <nav className="p-4 space-y-6 flex-1">
        {menuGroups.map((group) => (
          <div key={group.title} className="space-y-2">
            {/* Group Header */}
            <div className="px-3 py-2">
              <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                {group.title}
              </h3>
            </div>
            
            {/* Group Items */}
            <div className="space-y-1">
              {group.items.map((item) => {
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
            </div>
          </div>
        ))}
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
                {adminItem.badge && adminItem.badge.text && (
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
      case '/tickers/analysis':
        document.title = 'Altidus - Ticker Analysis';
        break;
      case '/tickers/compare':
        document.title = 'Altidus - Compare Tickers';
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
          <Route path="/tickers/analysis" element={<TickerAnalysisPage />} />
          <Route path="/tickers/compare" element={<CompareTickersPage />} />
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