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
  success: boolean;
  message: string;
  data: {
    totalReturn: string;
    annualizedReturn: string;
    volatility: string;
    sharpeRatio: string;
    maxDrawdown: string;
    sortinoRatio: string;
    calmarRatio: string;
    var95: string;
    beta: string;
    startValue: string;
    endValue: string;
    endValueAnalysis: string;
    endValueMissing: string;
  };
  warnings: {
    missingTickers: string[];
    tickersWithoutStartData: string[];
  };
  timeSeriesData: {
    portfolioValues: Record<string, number>;
    sp500Values: Record<string, number>;
    nasdaqValues: Record<string, number>;
  };
  failedTickers?: Array<{
    ticker: string;
    firstAvailableDate?: string;
  }>;
}

export interface TickerAnalysis {
  ticker: string;
  totalReturn: string;
  annualizedReturn: string;
  volatility: string;
  sharpeRatio: string;
  maxDrawdown: string;
  sortinoRatio: string;
  beta: string;
  var95: string;
  momentum12_1: string;
  dividendYield: string;
  dividendAmount: string;
  dividendFrequency: string;
  annualizedDividend: string;
  startPrice: string;
  endPrice: string;
  hasDataAtStart: boolean;
  firstAvailableDate?: string;
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
