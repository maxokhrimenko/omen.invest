import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import type { ApiError, ApiConfig } from '../types/api';
import type { Portfolio, PortfolioUploadResponse, PortfolioAnalysis, TickerAnalysis, CompareTickersResponse } from '../types/portfolio';
import { calculateAnalysisTimeout } from '../utils/timeoutCalculator';
import { logger } from '../utils/logger';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    const config: ApiConfig = {
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 300000, // 5 minutes for large portfolio analysis
      headers: {
        'Content-Type': 'application/json',
      },
    };

    this.api = axios.create(config);

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        logger.logApiCall(
          config.method?.toUpperCase() || 'UNKNOWN',
          config.url || 'unknown',
          undefined,
          undefined,
          { requestId: Math.random().toString(36).substr(2, 9) }
        );
        return config;
      },
      (error) => {
        logger.error('Request error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        logger.logApiCall(
          response.config.method?.toUpperCase() || 'UNKNOWN',
          response.config.url || 'unknown',
          response.status,
          undefined,
          { requestId: Math.random().toString(36).substr(2, 9) }
        );
        return response;
      },
      (error) => {
        logger.error('Response error', error, {
          url: error.config?.url,
          status: error.response?.status,
          method: error.config?.method
        });
        const apiError: ApiError = {
          message: error.response?.data?.message || error.message || 'An unexpected error occurred',
          status: error.response?.status,
          details: error.response?.data,
        };
        return Promise.reject(apiError);
      }
    );
  }

  // Getter for API instance (for administration page)
  getApiInstance(): AxiosInstance {
    return this.api;
  }

  // Portfolio endpoints
  async uploadPortfolio(file: File): Promise<PortfolioUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post<PortfolioUploadResponse>('/portfolio/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async getPortfolio(): Promise<Portfolio | null> {
    try {
      const response = await this.api.get<Portfolio>('/portfolio');
      return response.data;
    } catch (error: unknown) {
      // If it's a 404 error, that means no portfolio is loaded, which is a valid state
      if (error && typeof error === 'object' && 'status' in error && error.status === 404) {
        return null;
      }
      // For other errors, re-throw them
      throw error;
    }
  }

  async clearPortfolio(): Promise<{ success: boolean; message: string }> {
    const response = await this.api.delete<{ success: boolean; message: string }>('/portfolio');
    return response.data;
  }

  async analyzePortfolio(startDate: string, endDate: string, tickerCount?: number): Promise<PortfolioAnalysis> {
    // Calculate dynamic timeout if ticker count is provided
    let timeout = 300000; // Default 5 minutes
    if (tickerCount) {
      timeout = calculateAnalysisTimeout(tickerCount, startDate, endDate) * 1000; // Convert to milliseconds
    }
    
    const response = await this.api.get<PortfolioAnalysis>('/portfolio/analysis', {
      params: { start_date: startDate, end_date: endDate },
      timeout
    });
    return response.data;
  }

  async analyzeTickers(startDate: string, endDate: string, tickerCount?: number): Promise<{ data: TickerAnalysis[]; failedTickers?: Array<{ ticker: string; firstAvailableDate?: string }>; warnings?: { missingTickers: string[]; tickersWithoutStartData: string[]; firstAvailableDates: { [ticker: string]: string } } }> {
    // Calculate dynamic timeout if ticker count is provided
    let timeout = 300000; // Default 5 minutes
    if (tickerCount) {
      timeout = calculateAnalysisTimeout(tickerCount, startDate, endDate) * 1000; // Convert to milliseconds
    }
    
    const response = await this.api.get<{ success: boolean; message: string; data: TickerAnalysis[]; failedTickers?: Array<{ ticker: string; firstAvailableDate?: string }>; warnings?: { missingTickers: string[]; tickersWithoutStartData: string[]; firstAvailableDates: { [ticker: string]: string } } }>('/portfolio/tickers/analysis', {
      params: { start_date: startDate, end_date: endDate },
      timeout
    });
    return {
      data: response.data.data,
      failedTickers: response.data.failedTickers,
      warnings: response.data.warnings
    };
  }

  async compareTickers(startDate: string, endDate: string, tickerCount?: number): Promise<CompareTickersResponse> {
    // Calculate dynamic timeout if ticker count is provided
    let timeout = 300000; // Default 5 minutes
    if (tickerCount) {
      timeout = calculateAnalysisTimeout(tickerCount, startDate, endDate) * 1000; // Convert to milliseconds
    }
    
    const response = await this.api.post<CompareTickersResponse>('/portfolio/tickers/compare', {
      start_date: startDate,
      end_date: endDate
    }, {
      timeout
    });
    
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.api.get<{ status: string; timestamp: string }>('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
