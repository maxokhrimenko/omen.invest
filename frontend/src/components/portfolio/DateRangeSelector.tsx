import React, { useState, useEffect } from 'react';
import CalendarSelector from './CalendarSelector';
import { getPreviousWorkingDayString } from '../../utils/dateUtils';

export interface DateRange {
  startDate: string;
  endDate: string;
  label: string;
  type: 'preset' | 'custom';
}

interface DateRangeSelectorProps {
  selectedRange: DateRange | null;
  onRangeChange: (range: DateRange) => void;
}

const DateRangeSelector: React.FC<DateRangeSelectorProps> = ({
  selectedRange,
  onRangeChange
}) => {
  const [customStartDate] = useState(getDateString(12, 'months'));
  const [customEndDate] = useState(getDateString(0, 'days'));

  // Predefined date ranges
  const predefinedRanges: DateRange[] = [
    {
      startDate: getDateString(12, 'months'),
      endDate: getDateString(0, 'days'),
      label: '12 Months',
      type: 'preset'
    },
    {
      startDate: getDateString(24, 'months'),
      endDate: getDateString(0, 'days'),
      label: '24 Months',
      type: 'preset'
    },
    {
      startDate: getDateString(36, 'months'),
      endDate: getDateString(0, 'days'),
      label: '36 Months',
      type: 'preset'
    },
    {
      startDate: getDateString(48, 'months'),
      endDate: getDateString(0, 'days'),
      label: '48 Months',
      type: 'preset'
    },
    {
      startDate: getDateString(60, 'months'),
      endDate: getDateString(0, 'days'),
      label: '60 Months',
      type: 'preset'
    },
    {
      startDate: getThisYearToDateStart(),
      endDate: getPreviousWorkingDayString(),
      label: 'This year to date',
      type: 'preset'
    },
    {
      startDate: getPreviousYearStart(),
      endDate: getPreviousYearEnd(),
      label: 'Previous year',
      type: 'preset'
    }
  ];

  // Set default selection (12 Months)
  useEffect(() => {
    if (!selectedRange) {
      onRangeChange(predefinedRanges[0]); // 12 Months
    }
  }, [selectedRange, onRangeChange]);

  const handlePresetRange = (range: DateRange) => {
    onRangeChange(range);
  };

  const handleCalendarDateChange = (startDate: string, endDate: string) => {
    const newRange = {
      startDate,
      endDate,
      label: `${formatDate(startDate)} - ${formatDate(endDate)}`,
      type: 'custom' as const
    };
    onRangeChange(newRange);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="flex items-start space-x-6">
      {/* Predefined Ranges - Vertical */}
      <div className="w-32">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Time Period</h3>
        <div className="flex flex-col space-y-2">
          {predefinedRanges.map((range) => (
            <button
              key={range.label}
              onClick={() => handlePresetRange(range)}
              className={`px-2 py-2 text-xs font-medium rounded-lg border transition-all duration-200 ${
                selectedRange?.label === range.label
                  ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-sm'
                  : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Calendar Selector - Wider */}
      <div className="flex-1">
        <CalendarSelector
          startDate={selectedRange?.startDate || customStartDate}
          endDate={selectedRange?.endDate || customEndDate}
          onDateChange={handleCalendarDateChange}
        />
      </div>
    </div>
  );
};

// Helper function to calculate date strings
function getDateString(amount: number, unit: 'days' | 'months' | 'years', offset: number = 0): string {
  // For end dates (amount = 0, unit = 'days'), use previous working day
  if (amount === 0 && unit === 'days') {
    return getPreviousWorkingDayString();
  }
  
  const date = new Date();
  
  if (unit === 'days') {
    date.setDate(date.getDate() - amount + offset);
  } else if (unit === 'months') {
    date.setMonth(date.getMonth() - amount + offset);
  } else if (unit === 'years') {
    date.setFullYear(date.getFullYear() - amount + offset);
  }
  
  return date.toISOString().split('T')[0];
}

// Helper function to get start of current year (January 1st)
function getThisYearToDateStart(): string {
  const currentYear = new Date().getFullYear();
  const date = new Date(currentYear, 0, 1);
  // Use local date to avoid timezone issues
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Helper function to get start of previous year (January 1st of previous year)
function getPreviousYearStart(): string {
  const currentYear = new Date().getFullYear();
  const previousYear = currentYear - 1;
  const date = new Date(previousYear, 0, 1);
  // Use local date to avoid timezone issues
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Helper function to get end of previous year (December 31st of previous year)
function getPreviousYearEnd(): string {
  const currentYear = new Date().getFullYear();
  const previousYear = currentYear - 1;
  const date = new Date(previousYear, 11, 31);
  // Use local date to avoid timezone issues
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export default DateRangeSelector;
