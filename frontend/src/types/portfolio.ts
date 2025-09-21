export interface Position {
  ticker: string;
  position: number;
}

export interface Portfolio {
  positions: Position[];
  totalPositions: number;
  tickers: string[];
}

export interface PortfolioUploadResponse {
  success: boolean;
  message: string;
  portfolio?: Portfolio;
}

export interface PortfolioAnalysis {
  startValue: string;
  endValue: string;
  endValueAnalysis: string;
  endValueMissing: string;
  totalReturn: string;
  annualizedReturn: string;
  volatility: string;
  sharpeRatio: string;
  maxDrawdown: string;
  sortinoRatio: string;
  calmarRatio: string;
  var95: string;
  beta: string;
}

export interface TickerAnalysis {
  ticker: string;
  startPrice: string;
  endPrice: string;
  totalReturn: string;
  annualizedReturn: string;
  volatility: string;
  sharpeRatio: string;
  maxDrawdown: string;
  dividendYield: string;
  momentum12_1: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}
