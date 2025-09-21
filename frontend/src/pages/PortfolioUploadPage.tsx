import React, { useState, useEffect } from 'react';
import { Portfolio, ApiError } from '../../types/portfolio';
import { apiService } from '../../services/api';
import PortfolioUpload from '../components/portfolio/PortfolioUpload';
import PortfolioTable from '../components/portfolio/PortfolioTable';
import { AlertCircle, CheckCircle } from 'lucide-react';

const PortfolioUploadPage: React.FC = () => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load existing portfolio on component mount
  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const portfolioData = await apiService.getPortfolio();
      setPortfolio(portfolioData);
    } catch (error) {
      const apiError = error as ApiError;
      // Don't show error if no portfolio exists (404 is expected)
      if (apiError.status !== 404) {
        setError(apiError.message || 'Failed to load portfolio');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = (uploadedPortfolio: Portfolio) => {
    setPortfolio(uploadedPortfolio);
    setSuccess('Portfolio uploaded successfully!');
    setError(null);
    
    // Clear success message after 3 seconds
    setTimeout(() => setSuccess(null), 3000);
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
    setSuccess(null);
    
    // Clear error message after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const handleClearPortfolio = async () => {
    try {
      setError(null);
      await apiService.clearPortfolio();
      setPortfolio(null);
      setSuccess('Portfolio cleared successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      const apiError = error as ApiError;
      setError(apiError.message || 'Failed to clear portfolio');
    }
  };

  const handleRefreshPortfolio = async () => {
    setIsRefreshing(true);
    await loadPortfolio();
    setIsRefreshing(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Success/Error Messages */}
      {success && (
        <div className="bg-success-50 border border-success-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-success-600" />
            <p className="text-sm font-medium text-success-800">{success}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-error-50 border border-error-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-error-600" />
            <p className="text-sm font-medium text-error-800">{error}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      {portfolio ? (
        <PortfolioTable
          portfolio={portfolio}
          onClearPortfolio={handleClearPortfolio}
          onRefreshPortfolio={handleRefreshPortfolio}
          isRefreshing={isRefreshing}
        />
      ) : (
        <PortfolioUpload
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />
      )}
    </div>
  );
};

export default PortfolioUploadPage;
