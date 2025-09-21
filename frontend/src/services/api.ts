import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import type { ApiError, ApiConfig } from '../types/api';
import type { Portfolio, PortfolioUploadResponse, PortfolioAnalysis, TickerAnalysis } from '../types/portfolio';
import { calculateAnalysisTimeout, formatTimeout } from '../utils/timeoutCalculator';

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
        console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
        return config;
      },
      (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`Response received from ${response.config.url}:`, response.status);
        return response;
      },
      (error) => {
        console.error('Response error:', error);
        const apiError: ApiError = {
          message: error.response?.data?.message || error.message || 'An unexpected error occurred',
          status: error.response?.status,
          details: error.response?.data,
        };
        return Promise.reject(apiError);
      }
    );
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
    } catch (error: any) {
      // If it's a 404 error, that means no portfolio is loaded, which is a valid state
      if (error.status === 404) {
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
    console.log('Calling analyzePortfolio API...', { startDate, endDate });
    
    // Calculate dynamic timeout if ticker count is provided
    let timeout = 300000; // Default 5 minutes
    if (tickerCount) {
      timeout = calculateAnalysisTimeout(tickerCount, startDate, endDate) * 1000; // Convert to milliseconds
      console.log(`Using dynamic timeout: ${formatTimeout(timeout / 1000)} for ${tickerCount} tickers`);
    }
    
    const response = await this.api.get<PortfolioAnalysis>('/portfolio/analysis', {
      params: { start_date: startDate, end_date: endDate },
      timeout
    });
    console.log('analyzePortfolio response:', response.data);
    return response.data;
  }

  async analyzeTickers(startDate: string, endDate: string, tickerCount?: number): Promise<{ data: TickerAnalysis[]; failedTickers?: Array<{ ticker: string; firstAvailableDate?: string }> }> {
    console.log('Calling analyzeTickers API...', { startDate, endDate });
    
    // Calculate dynamic timeout if ticker count is provided
    let timeout = 300000; // Default 5 minutes
    if (tickerCount) {
      timeout = calculateAnalysisTimeout(tickerCount, startDate, endDate) * 1000; // Convert to milliseconds
      console.log(`Using dynamic timeout: ${formatTimeout(timeout / 1000)} for ${tickerCount} tickers`);
    }
    
    const response = await this.api.get<{ success: boolean; message: string; data: TickerAnalysis[]; failedTickers?: Array<{ ticker: string; firstAvailableDate?: string }> }>('/portfolio/tickers/analysis', {
      params: { start_date: startDate, end_date: endDate },
      timeout
    });
    console.log('analyzeTickers response:', { 
      success: response.data.success, 
      tickerCount: response.data.data.length,
      failedTickers: response.data.failedTickers?.length || 0
    });
    return {
      data: response.data.data,
      failedTickers: response.data.failedTickers
    };
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.api.get<{ status: string; timestamp: string }>('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
