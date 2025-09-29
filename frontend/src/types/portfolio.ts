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
    dividendAmount: string;
    annualizedDividendYield: string;
    totalDividendYield: string;
  };
  warnings: {
    missingTickers: string[];
    tickersWithoutStartData: string[];
    firstAvailableDates?: { [ticker: string]: string };
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
  momentum12to1: string;
  dividendYield: string;
  dividendAmount: string;
  dividendFrequency: string;
  annualizedDividend: string;
  startPrice: string;
  endPrice: string;
  hasDataAtStart: boolean;
  firstAvailableDate?: string;
  position?: number;
  marketValue?: string;
  // Advanced metrics
  calmarRatio: string;
  ulcerIndex: string;
  timeUnderWater: string;
  cvar95: string;
  correlationToPortfolio: string;
  riskContributionAbsolute: string;
  riskContributionPercent: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

// Compare Tickers Types
export interface TickerComparisonData {
  ticker: string;
  annualizedReturn: string;
  sharpeRatio: string;
  volatility: string;
  maxDrawdown: string;
  sortinoRatio: string;
  calmarRatio: string;
  ulcerIndex: string;
  timeUnderWater: string;
  cvar95: string;
  correlationToPortfolio: string;
  riskContributionPercent: string;
}

export interface CompareTickersResults {
  metrics: TickerAnalysis[];
  bestPerformers: TickerComparisonData[];
  worstPerformers: TickerComparisonData[];
  bestSharpe: TickerComparisonData[];
  lowestRisk: TickerComparisonData[];
  // Advanced metrics rankings
  bestCalmar: TickerComparisonData[];
  worstCalmar: TickerComparisonData[];
  bestSortino: TickerComparisonData[];
  worstSortino: TickerComparisonData[];
  bestMaxDrawdown: TickerComparisonData[];
  worstMaxDrawdown: TickerComparisonData[];
  bestUlcer: TickerComparisonData[];
  worstUlcer: TickerComparisonData[];
  bestTimeUnderWater: TickerComparisonData[];
  worstTimeUnderWater: TickerComparisonData[];
  bestCvar: TickerComparisonData[];
  worstCvar: TickerComparisonData[];
  bestCorrelation: TickerComparisonData[];
  worstCorrelation: TickerComparisonData[];
  bestRiskContribution: TickerComparisonData[];
  worstRiskContribution: TickerComparisonData[];
}

export interface CompareTickersResponse {
  success: boolean;
  message: string;
  data: CompareTickersResults;
  warnings: {
    missingTickers: string[];
    tickersWithoutStartData: string[];
    firstAvailableDates: { [ticker: string]: string };
  };
  failedTickers?: Array<{
    ticker: string;
    firstAvailableDate?: string;
  }>;
}
