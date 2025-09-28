import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import PortfolioAnalysisPage from './pages/PortfolioAnalysisPage';
import TickerAnalysisPage from './pages/TickerAnalysisPage';
import CompareTickersPage from './pages/CompareTickersPage';
import AdministrationPage from './pages/AdministrationPage';
import { apiService } from './services/api';
import Sidebar from './components/layout/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './contexts/ToastContext';





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
          <Route path="/tickers/compare" element={<CompareTickersPage portfolio={portfolio} />} />
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