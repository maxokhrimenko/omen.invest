import React, { useState } from 'react';
import { Trash2, Database, BarChart3, AlertTriangle, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';

interface TickerOption {
  value: string;
  label: string;
}

const AdministrationPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<{ [key: string]: boolean }>({});
  const [showConfirmModal, setShowConfirmModal] = useState<{ [key: string]: boolean }>({});
  const [tickerInput, setTickerInput] = useState('');
  const [tickerOptions, setTickerOptions] = useState<TickerOption[]>([]);
  const [showTickerDropdown, setShowTickerDropdown] = useState(false);
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);

  const setLoading = (key: string, loading: boolean) => {
    setIsLoading(prev => ({ ...prev, [key]: loading }));
  };

  const showModal = (key: string) => {
    setShowConfirmModal(prev => ({ ...prev, [key]: true }));
  };

  const hideModal = (key: string) => {
    setShowConfirmModal(prev => ({ ...prev, [key]: false }));
  };

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    // Simple toast implementation - you might want to use a proper toast library
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${
      type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  };

  const handleLogsClearAll = async () => {
    setLoading('logs-clear', true);
    try {
      const response = await apiService.getApiInstance().post('/api/admin/logs/clear-all');
      
      if (response.data.success) {
        showToast('All logs cleared successfully');
      } else {
        showToast('Error clearing logs', 'error');
      }
    } catch (error) {
      showToast('Error clearing logs', 'error');
    } finally {
      setLoading('logs-clear', false);
      hideModal('logs-clear');
    }
  };

  const handleWarehouseClearAll = async () => {
    setLoading('warehouse-clear', true);
    try {
      const response = await apiService.getApiInstance().post('/api/admin/warehouse/clear-all');
      
      if (response.data.success) {
        showToast('All warehouse data cleared successfully');
      } else {
        showToast('Error clearing warehouse data', 'error');
      }
    } catch (error) {
      showToast('Error clearing warehouse data', 'error');
    } finally {
      setLoading('warehouse-clear', false);
      hideModal('warehouse-clear');
    }
  };

  const handleWarehouseStats = async () => {
    setLoading('warehouse-stats', true);
    try {
      const response = await apiService.getApiInstance().get('/api/admin/warehouse/stats');
      
      if (response.data.success) {
        const data = response.data.data;
        showToast(`Warehouse stats: ${data.ticker_count || 0} tickers, ${data.total_records || 0} records`);
      } else {
        showToast('Error fetching warehouse stats', 'error');
      }
    } catch (error) {
      showToast('Error fetching warehouse stats', 'error');
    } finally {
      setLoading('warehouse-stats', false);
    }
  };

  const handleTickerInputChange = async (value: string) => {
    setTickerInput(value);
    
    // Always fetch tickers, whether there's a search term or not
    try {
      const response = await apiService.getApiInstance().get('/api/admin/warehouse/tickers', {
        params: { search: value }
      });
      if (response.data.success) {
        setTickerOptions(response.data.tickers || []);
        setShowTickerDropdown(true);
      }
    } catch (error) {
      // Silent fail for search
    }
  };

  const handleTickerInputFocus = async () => {
    // When input is focused, show all tickers if not already loaded
    if (tickerOptions.length === 0) {
      try {
        const response = await apiService.getApiInstance().get('/api/admin/warehouse/tickers');
        if (response.data.success) {
          setTickerOptions(response.data.tickers || []);
        }
      } catch (error) {
        // Silent fail
      }
    }
    setShowTickerDropdown(true);
  };

  const handleTickerInputBlur = () => {
    // Hide dropdown when input loses focus
    // Use setTimeout to allow click events on dropdown items to fire first
    setTimeout(() => {
      setShowTickerDropdown(false);
    }, 150);
  };

  const handleTickerSelect = (ticker: TickerOption) => {
    if (!selectedTickers.includes(ticker.value)) {
      setSelectedTickers([...selectedTickers, ticker.value]);
    }
    setTickerInput('');
    // Keep dropdown open for continuous selection
    setShowTickerDropdown(true);
  };

  const handleTickerRemove = (tickerToRemove: string) => {
    setSelectedTickers(selectedTickers.filter(ticker => ticker !== tickerToRemove));
  };

  const handleSelectAll = async () => {
    try {
      const response = await apiService.getApiInstance().get('/api/admin/warehouse/tickers');
      if (response.data.success) {
        const allTickers = response.data.tickers.map((t: TickerOption) => t.value);
        setSelectedTickers(allTickers);
      }
    } catch (error) {
      // Silent fail
    }
  };

  const handleClearSelection = () => {
    setSelectedTickers([]);
  };

  const handleWarehouseClearTicker = async () => {
    if (selectedTickers.length === 0) {
      showToast('Please select at least one ticker', 'error');
      return;
    }

    setLoading('warehouse-clear-ticker', true);
    try {
      // Clear data for each selected ticker
      const clearPromises = selectedTickers.map(ticker => 
        apiService.getApiInstance().post('/api/admin/warehouse/clear-ticker', {
          ticker: ticker
        })
      );
      
      const results = await Promise.all(clearPromises);
      const successCount = results.filter(r => r.data.success).length;
      
      if (successCount === selectedTickers.length) {
        showToast(`Data cleared for ${selectedTickers.length} ticker(s): ${selectedTickers.join(', ')}`);
        setSelectedTickers([]);
        setTickerInput('');
      } else {
        showToast(`Cleared data for ${successCount} of ${selectedTickers.length} tickers`, 'error');
      }
    } catch (error) {
      showToast('Error clearing ticker data', 'error');
    } finally {
      setLoading('warehouse-clear-ticker', false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Administration
          </h1>
          <p className="text-gray-600">
            System administration and configuration
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Logs Management Block */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-6">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Logs Management</h2>
                <p className="text-sm text-gray-500">Clear application logs</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <button
                onClick={() => showModal('logs-clear')}
                disabled={isLoading['logs-clear']}
                className="w-full flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading['logs-clear'] ? (
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                ) : (
                  <Trash2 className="w-5 h-5 mr-2" />
                )}
                Clear All Logs
              </button>
            </div>
          </div>

          {/* Warehouse Management Block */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <Database className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Warehouse Management</h2>
                <p className="text-sm text-gray-500">Manage warehouse data</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <button
                onClick={() => showModal('warehouse-clear')}
                disabled={isLoading['warehouse-clear']}
                className="w-full flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading['warehouse-clear'] ? (
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                ) : (
                  <Trash2 className="w-5 h-5 mr-2" />
                )}
                Clear All Warehouse Data
              </button>

              <button
                onClick={handleWarehouseStats}
                disabled={isLoading['warehouse-stats']}
                className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading['warehouse-stats'] ? (
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                ) : (
                  <BarChart3 className="w-5 h-5 mr-2" />
                )}
                Show Warehouse Stats
              </button>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Clear Specific Tickers
                    </label>
                    <p className="text-xs text-gray-500 mt-1">Select tickers to remove from warehouse</p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={handleSelectAll}
                      className="inline-flex items-center px-3 py-1.5 text-sm bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                    >
                      Select All
                    </button>
                    <button
                      onClick={handleClearSelection}
                      className="inline-flex items-center px-3 py-1.5 text-sm bg-white text-gray-700 font-medium rounded-md border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                    >
                      Clear Selection
                    </button>
                  </div>
                </div>
                
                {/* Multi-select input with inline display */}
                <div className="relative">
                  <div className="w-full min-h-[40px] px-3 py-2 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 flex flex-wrap items-center gap-1">
                    {/* Selected tickers as removable tags */}
                    {selectedTickers.map((ticker) => (
                      <span
                        key={ticker}
                        className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-md"
                      >
                        {ticker}
                        <button
                          onClick={() => handleTickerRemove(ticker)}
                          className="ml-1 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                    
                    {/* Input field for typing new tickers */}
                    <input
                      type="text"
                      value={tickerInput}
                      onChange={(e) => handleTickerInputChange(e.target.value)}
                      onFocus={handleTickerInputFocus}
                      onBlur={handleTickerInputBlur}
                      placeholder={selectedTickers.length === 0 ? "Type to search tickers..." : ""}
                      className="flex-1 min-w-[120px] border-none outline-none bg-transparent"
                    />
                  </div>
                  
                  {showTickerDropdown && tickerOptions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {tickerOptions.map((option) => {
                        const isSelected = selectedTickers.includes(option.value);
                        return (
                          <button
                            key={option.value}
                            onMouseDown={(e) => e.preventDefault()} // Prevent input blur
                            onClick={() => handleTickerSelect(option)}
                            className={`w-full px-3 py-2 text-left focus:outline-none flex items-center justify-between ${
                              isSelected
                                ? 'bg-blue-50 text-blue-800 border-l-4 border-blue-500'
                                : 'hover:bg-gray-100 focus:bg-gray-100'
                            }`}
                          >
                            <span>{option.label}</span>
                            {isSelected && (
                              <span className="text-blue-600 text-sm">✓</span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
                
                <button
                  onClick={handleWarehouseClearTicker}
                  disabled={isLoading['warehouse-clear-ticker'] || selectedTickers.length === 0}
                  className="w-full flex items-center justify-center px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading['warehouse-clear-ticker'] ? (
                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  ) : (
                    <Trash2 className="w-5 h-5 mr-2" />
                  )}
                  Clear Ticker Data ({selectedTickers.length})
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Confirmation Modals */}
        {showConfirmModal['logs-clear'] && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <div className="flex items-center mb-4">
                <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">Clear All Logs</h3>
              </div>
              <p className="text-gray-600 mb-6">
                This will permanently delete all application logs. This action cannot be undone.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => hideModal('logs-clear')}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleLogsClearAll}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Clear Logs
                </button>
              </div>
            </div>
          </div>
        )}

        {showConfirmModal['warehouse-clear'] && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <div className="flex items-center mb-4">
                <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">Clear All Warehouse Data</h3>
              </div>
              <p className="text-gray-600 mb-6">
                This will permanently delete all warehouse data including market data, dividends, and benchmarks. This action cannot be undone.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => hideModal('warehouse-clear')}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleWarehouseClearAll}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Clear Data
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdministrationPage;
