import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ChartDataPoint {
  date: string;
  displayDate: string;
  portfolio: number | null;
  sp500: number | null;
  nasdaq: number | null;
}

interface PortfolioChartProps {
  portfolioValues: Record<string, number>;
  sp500Values: Record<string, number>;
  nasdaqValues: Record<string, number>;
  startValue: number;
}

const PortfolioChart: React.FC<PortfolioChartProps> = ({ 
  portfolioValues, 
  sp500Values, 
  nasdaqValues, 
  startValue 
}) => {
  // Normalize all values to start at the same point
  const normalizeValues = (values: Record<string, number>, startValue: number) => {
    const entries = Object.entries(values).sort(([a], [b]) => a.localeCompare(b));
    if (entries.length === 0) return {};
    
    const firstValue = entries[0][1];
    const normalized: Record<string, number> = {};
    
    entries.forEach(([date, value]) => {
      normalized[date] = startValue * (value / firstValue);
    });
    
    return normalized;
  };

  const normalizedPortfolio = normalizeValues(portfolioValues, startValue);
  const normalizedSp500 = normalizeValues(sp500Values, startValue);
  const normalizedNasdaq = normalizeValues(nasdaqValues, startValue);

  // Get all unique dates
  const allDates = new Set([
    ...Object.keys(normalizedPortfolio),
    ...Object.keys(normalizedSp500),
    ...Object.keys(normalizedNasdaq)
  ]);

  // Create chart data
  const chartData: ChartDataPoint[] = Array.from(allDates)
    .sort((a, b) => new Date(a).getTime() - new Date(b).getTime())
    .map(date => {
      const dateObj = new Date(date);
      return {
        date: date, // Keep original date string for data consistency
        displayDate: dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        portfolio: normalizedPortfolio[date] || null,
        sp500: normalizedSp500[date] || null,
        nasdaq: normalizedNasdaq[date] || null
      };
    });

  const formatValue = (value: number) => `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

  // Calculate percentage change from start value
  const calculatePercentageChange = (currentValue: number, startValue: number) => {
    return ((currentValue - startValue) / startValue) * 100;
  };

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{`Date: ${label}`}</p>
          {payload.map((entry: any, index: number) => {
            if (entry.value === null) return null;
            const percentageChange = calculatePercentageChange(entry.value, startValue);
            const isPositive = percentageChange >= 0;
            return (
              <p key={index} className="text-sm" style={{ color: entry.color }}>
                <span className="font-medium">{entry.name}:</span> {formatValue(entry.value)} 
                <span className={`ml-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  ({isPositive ? '+' : ''}{percentageChange.toFixed(2)}%)
                </span>
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  // Custom tick formatter to show fewer labels
  const formatXAxisTick = (tickItem: any, index: number) => {
    const totalTicks = finalChartData.length;
    const maxTicks = 6; // Maximum number of ticks to show
    const interval = Math.ceil(totalTicks / maxTicks);
    
    // Always show first and last
    if (index === 0 || index === totalTicks - 1) {
      return tickItem;
    }
    
    // Show every nth tick based on interval
    if (index % interval === 0) {
      return tickItem;
    }
    
    return '';
  };

  // Debug logging
  console.log('Chart Debug:', {
    portfolioValues: Object.keys(portfolioValues).length,
    sp500Values: Object.keys(sp500Values).length,
    nasdaqValues: Object.keys(nasdaqValues).length,
    startValue,
    normalizedPortfolio: Object.keys(normalizedPortfolio).length,
    normalizedSp500: Object.keys(normalizedSp500).length,
    normalizedNasdaq: Object.keys(normalizedNasdaq).length,
    allDates: Array.from(allDates).length,
    chartDataLength: chartData.length,
    chartData: chartData.slice(0, 3),
    lastFewDates: chartData.slice(-3)
  });

  // Create test data if no real data
  const testData = [
    { date: '2024-01-01', displayDate: 'Jan 1, 2024', portfolio: 1000, sp500: 1000, nasdaq: 1000 },
    { date: '2024-01-02', displayDate: 'Jan 2, 2024', portfolio: 1050, sp500: 1020, nasdaq: 1010 },
    { date: '2024-01-03', displayDate: 'Jan 3, 2024', portfolio: 1100, sp500: 1040, nasdaq: 1020 },
    { date: '2024-01-04', displayDate: 'Jan 4, 2024', portfolio: 1080, sp500: 1030, nasdaq: 1015 },
    { date: '2024-01-05', displayDate: 'Jan 5, 2024', portfolio: 1120, sp500: 1050, nasdaq: 1030 }
  ];

  const finalChartData = chartData.length > 0 ? chartData : testData;

  if (chartData.length === 0) {
    console.log('Using test data for chart');
  }

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={finalChartData} margin={{ top: 30, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="displayDate" 
            stroke="#666"
            fontSize={10}
            tickLine={false}
            axisLine={false}
            angle={-30}
            textAnchor="end"
            height={60}
            interval={0}
            tick={{ fontSize: 9 }}
            tickFormatter={formatXAxisTick}
          />
          <YAxis 
            stroke="#666"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={formatValue}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="portfolio"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Portfolio"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="sp500"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="S&P 500"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="nasdaq"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={false}
            name="NASDAQ"
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PortfolioChart;
