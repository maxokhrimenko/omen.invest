import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiError, ApiConfig } from '../types/api';
import { Portfolio, PortfolioUploadResponse, PortfolioAnalysis, TickerAnalysis } from '../types/portfolio';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    const config: ApiConfig = {
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      timeout: 30000,
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

  async getPortfolio(): Promise<Portfolio> {
    const response = await this.api.get<Portfolio>('/portfolio');
    return response.data;
  }

  async clearPortfolio(): Promise<{ success: boolean; message: string }> {
    const response = await this.api.delete<{ success: boolean; message: string }>('/portfolio');
    return response.data;
  }

  async analyzePortfolio(): Promise<PortfolioAnalysis> {
    const response = await this.api.get<PortfolioAnalysis>('/portfolio/analysis');
    return response.data;
  }

  async analyzeTickers(): Promise<TickerAnalysis[]> {
    const response = await this.api.get<TickerAnalysis[]>('/portfolio/tickers/analysis');
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
