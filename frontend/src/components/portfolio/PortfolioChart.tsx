import React, { useMemo, useCallback } from 'react';
import { TrendingUp, Building2, BarChart3 } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

interface ChartDataPoint {
  date: string;
  portfolio: number | null;
  sp500: number | null;
  nasdaq: number | null;
  displayDate: string;
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

  // Process and normalize data
  const chartData = useMemo(() => {
    // Get all unique dates from all datasets
    const allDates = new Set([
      ...Object.keys(portfolioValues),
      ...Object.keys(sp500Values),
      ...Object.keys(nasdaqValues)
    ]);

    // Sort dates chronologically
    const sortedDates = Array.from(allDates).sort((a, b) => 
      new Date(a).getTime() - new Date(b).getTime()
    );

    // If no real data, return test data
    if (sortedDates.length === 0) {
      return [
        { date: '2024-01-01', portfolio: 1000, sp500: 1000, nasdaq: 1000, displayDate: 'Jan 1, 24' },
        { date: '2024-01-02', portfolio: 1050, sp500: 1020, nasdaq: 1010, displayDate: 'Jan 2, 24' },
        { date: '2024-01-03', portfolio: 1100, sp500: 1040, nasdaq: 1020, displayDate: 'Jan 3, 24' },
        { date: '2024-01-04', portfolio: 1080, sp500: 1030, nasdaq: 1015, displayDate: 'Jan 4, 24' },
        { date: '2024-01-05', portfolio: 1120, sp500: 1050, nasdaq: 1030, displayDate: 'Jan 5, 24' },
        { date: '2024-01-08', portfolio: 1150, sp500: 1060, nasdaq: 1040, displayDate: 'Jan 8, 24' },
        { date: '2024-01-09', portfolio: 1130, sp500: 1055, nasdaq: 1035, displayDate: 'Jan 9, 24' },
        { date: '2024-01-10', portfolio: 1180, sp500: 1070, nasdaq: 1050, displayDate: 'Jan 10, 24' },
        { date: '2024-01-11', portfolio: 1200, sp500: 1080, nasdaq: 1060, displayDate: 'Jan 11, 24' },
        { date: '2024-01-12', portfolio: 1220, sp500: 1090, nasdaq: 1070, displayDate: 'Jan 12, 24' }
      ];
    }

    // Find the first available value for each dataset to use as normalization base
    const portfolioFirstDate = sortedDates.find(date => portfolioValues[date]);
    const sp500FirstDate = sortedDates.find(date => sp500Values[date]);
    const nasdaqFirstDate = sortedDates.find(date => nasdaqValues[date]);
    
    const portfolioFirstValue = portfolioFirstDate ? portfolioValues[portfolioFirstDate] : startValue;
    const sp500FirstValue = sp500FirstDate ? sp500Values[sp500FirstDate] : startValue;
    const nasdaqFirstValue = nasdaqFirstDate ? nasdaqValues[nasdaqFirstDate] : startValue;


    // Create normalized data points
    const data: ChartDataPoint[] = sortedDates.map(date => {
      const dateObj = new Date(date);
      
      // Normalize values to start at the same point
      const portfolioValue = portfolioValues[date] 
        ? startValue * (portfolioValues[date] / portfolioFirstValue)
        : null;
      const sp500Value = sp500Values[date] 
        ? startValue * (sp500Values[date] / sp500FirstValue)
        : null;
      const nasdaqValue = nasdaqValues[date] 
        ? startValue * (nasdaqValues[date] / nasdaqFirstValue)
        : null;

      return {
        date,
        portfolio: portfolioValue,
        sp500: sp500Value,
        nasdaq: nasdaqValue,
        displayDate: dateObj.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric',
          year: '2-digit'
        })
      };
    });


    return data;
  }, [portfolioValues, sp500Values, nasdaqValues, startValue]);

  // Custom tooltip component
  const CustomTooltip = useCallback(({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; dataKey: string; color: string }>; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">{label}</p>
          {payload.map((entry: { value: number; dataKey: string; color: string }, index: number) => {
            if (entry.value === null) return null;
            
            const percentageChange = ((entry.value - startValue) / startValue) * 100;
            const isPositive = percentageChange >= 0;
            const sign = isPositive ? '+' : '';
            
            return (
              <p key={index} className="text-sm" style={{ color: entry.color }}>
                <span className="font-medium">{entry.dataKey}:</span> 
                <span className="ml-2">
                  ${entry.value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
                <span className={`ml-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  ({sign}{percentageChange.toFixed(2)}%)
                </span>
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  }, [startValue]);

  // Custom X-axis tick formatter
  const formatXAxisTick = useCallback((tickItem: string) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  }, []);

  // Custom Y-axis tick formatter
  const formatYAxisTick = useCallback((value: number) => {
    return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  }, []);

  // Custom Legend Component
  const CustomLegend = () => (
    <div className="flex justify-center items-center gap-6 mt-2">
      <div className="flex items-center gap-2">
        <TrendingUp className="w-4 h-4 text-blue-600" />
        <span className="text-sm font-medium text-gray-700">Portfolio</span>
      </div>
      <div className="flex items-center gap-2">
        <Building2 className="w-4 h-4 text-green-600" />
        <span className="text-sm font-medium text-gray-700">S&P 500</span>
      </div>
      <div className="flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-orange-500" />
        <span className="text-sm font-medium text-gray-700">NASDAQ</span>
      </div>
    </div>
  );

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{
              top: 10,
              right: 30,
              left: 20,
              bottom: 10,
            }}
          >
            <CartesianGrid 
              strokeDasharray="2 4" 
              stroke="#e2e8f0" 
              strokeOpacity={0.4}
              vertical={false}
            />
            
            <XAxis
              dataKey="date"
              type="category"
              tickFormatter={formatXAxisTick}
              tick={{ fontSize: 11, fill: '#64748b', fontWeight: '500' }}
              axisLine={{ stroke: '#e2e8f0', strokeWidth: 1 }}
              tickLine={{ stroke: '#e2e8f0', strokeWidth: 1 }}
              interval="preserveStartEnd"
              minTickGap={50}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            
            <YAxis
              tickFormatter={formatYAxisTick}
              tick={{ fontSize: 11, fill: '#64748b', fontWeight: '500' }}
              axisLine={{ stroke: '#e2e8f0', strokeWidth: 1 }}
              tickLine={{ stroke: '#e2e8f0', strokeWidth: 1 }}
              domain={[0, 'dataMax + 100']}
              tickCount={6}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            {/* Reference line at start value */}
            <ReferenceLine 
              y={startValue} 
              stroke="#6366f1" 
              strokeDasharray="4 4" 
              strokeWidth={2}
              strokeOpacity={0.8}
            />
            
            
            <Line
              type="monotone"
              dataKey="portfolio"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              connectNulls={true}
              name="Portfolio"
            />
            
            <Line
              type="monotone"
              dataKey="sp500"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, stroke: '#10b981', strokeWidth: 2 }}
              connectNulls={true}
              name="S&P 500"
            />
            
            <Line
              type="monotone"
              dataKey="nasdaq"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, stroke: '#f59e0b', strokeWidth: 2 }}
              connectNulls={true}
              name="NASDAQ"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Custom Legend - positioned at bottom within container */}
      <div className="flex-shrink-0 px-4 pt-3 pb-6">
        <CustomLegend />
      </div>
    </div>
  );
};

export default PortfolioChart;