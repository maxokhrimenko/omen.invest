import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Edit3 } from 'lucide-react';

interface CalendarSelectorProps {
  startDate: string;
  endDate: string;
  onDateChange: (startDate: string, endDate: string) => void;
}

const CalendarSelector: React.FC<CalendarSelectorProps> = ({
  startDate,
  endDate,
  onDateChange
}) => {
  const [startYear, setStartYear] = useState(new Date().getFullYear());
  const [startMonth, setStartMonth] = useState(new Date().getMonth());
  const [endYear, setEndYear] = useState(new Date().getFullYear());
  const [endMonth, setEndMonth] = useState(new Date().getMonth());
  const [selectedStartDate, setSelectedStartDate] = useState<Date | null>(null);
  const [selectedEndDate, setSelectedEndDate] = useState<Date | null>(null);
  const [startYearInput, setStartYearInput] = useState(new Date().getFullYear().toString());
  const [endYearInput, setEndYearInput] = useState(new Date().getFullYear().toString());

  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  // Always show current year and 4 years before it
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  useEffect(() => {
    if (startDate) {
      const date = new Date(startDate);
      setSelectedStartDate(date);
      setStartYear(date.getFullYear());
      setStartMonth(date.getMonth());
      setStartYearInput(date.getFullYear().toString());
    }
    if (endDate) {
      const date = new Date(endDate);
      setSelectedEndDate(date);
      setEndYear(date.getFullYear());
      setEndMonth(date.getMonth());
      setEndYearInput(date.getFullYear().toString());
    }
  }, [startDate, endDate]);

  // Sync input values when year changes from preset buttons
  useEffect(() => {
    setStartYearInput(startYear.toString());
  }, [startYear]);

  useEffect(() => {
    setEndYearInput(endYear.toString());
  }, [endYear]);

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month, 1).getDay();
  };

  const handleStartDateClick = (year: number, month: number, day: number) => {
    const clickedDate = new Date(year, month, day);
    setSelectedStartDate(clickedDate);
    
    // Format date as YYYY-MM-DD to avoid timezone issues
    const formattedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    
    onDateChange(
      formattedDate,
      selectedEndDate ? selectedEndDate.toISOString().split('T')[0] : endDate
    );
  };

  const handleEndDateClick = (year: number, month: number, day: number) => {
    const clickedDate = new Date(year, month, day);
    setSelectedEndDate(clickedDate);
    
    // Format date as YYYY-MM-DD to avoid timezone issues
    const formattedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    
    onDateChange(
      selectedStartDate ? selectedStartDate.toISOString().split('T')[0] : startDate,
      formattedDate
    );
  };

  const generateCalendarDays = (year: number, month: number) => {
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }

    return days;
  };


  const isDateInFuture = (year: number, month: number, day: number) => {
    const date = new Date(year, month, day);
    const today = new Date();
    today.setHours(23, 59, 59, 999); // End of today
    return date > today;
  };

  const isStartDateSelected = (year: number, month: number, day: number) => {
    if (!selectedStartDate) return false;
    return year === selectedStartDate.getFullYear() && 
           month === selectedStartDate.getMonth() && 
           day === selectedStartDate.getDate();
  };

  const isEndDateSelected = (year: number, month: number, day: number) => {
    if (!selectedEndDate) return false;
    return year === selectedEndDate.getFullYear() && 
           month === selectedEndDate.getMonth() && 
           day === selectedEndDate.getDate();
  };

  const startCalendarDays = generateCalendarDays(startYear, startMonth);
  const endCalendarDays = generateCalendarDays(endYear, endMonth);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-700">Date Range</h3>
        <CalendarIcon className="w-4 h-4 text-gray-400" />
      </div>

      <div className="flex space-x-6">
        {/* Start Date Calendar */}
        <div className="flex-1 bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="text-center mb-3">
            <h4 className="text-sm font-medium text-gray-700">Start Date</h4>
          </div>
          
          <div className="flex space-x-2">
            {/* Year Selection */}
            <div className="w-16">
              <label className="block text-xs font-medium text-gray-600 mb-2">Year</label>
              <div className="space-y-1">
                {years.map((year) => (
                  <button
                    key={year}
                    onClick={() => setStartYear(year)}
                    className={`w-full px-2 py-1 text-xs rounded transition-colors ${
                      year === startYear
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {year}
                  </button>
                ))}
                {/* Custom Year Input */}
                <div className="pt-2 border-t border-gray-200">
                  <div className="relative">
                    <Edit3 className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-400" />
                    <input
                      type="number"
                      value={startYearInput}
                      onChange={(e) => {
                        setStartYearInput(e.target.value);
                        const year = parseInt(e.target.value);
                        const currentYear = new Date().getFullYear();
                        if (!isNaN(year) && year >= 2000 && year <= currentYear) {
                          setStartYear(year);
                        }
                      }}
                      onBlur={(e) => {
                        const year = parseInt(e.target.value);
                        const currentYear = new Date().getFullYear();
                        if (isNaN(year) || year < 2000 || year > currentYear) {
                          setStartYearInput(startYear.toString());
                        }
                      }}
                      placeholder="Year"
                      className={`w-full pl-6 pr-2 py-1 text-xs border rounded text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none ${
                        (() => {
                          const year = parseInt(startYearInput);
                          const currentYear = new Date().getFullYear();
                          return isNaN(year) || year < 2000 || year > currentYear
                            ? 'border-red-300 text-red-600 bg-red-50 focus:ring-red-500 focus:border-red-500'
                            : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500';
                        })()
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Month Selection */}
            <div className="w-20">
              <label className="block text-xs font-medium text-gray-600 mb-2">Month</label>
              <div className="grid grid-cols-2 gap-1">
                {months.map((month, index) => (
                  <button
                    key={month}
                    onClick={() => setStartMonth(index)}
                    className={`px-2 py-1 text-xs rounded transition-colors w-full ${
                      index === startMonth
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {month}
                  </button>
                ))}
              </div>
            </div>

            {/* Calendar Grid */}
            <div className="flex-1">
              <div className="grid grid-cols-7 gap-1">
                {/* Day headers */}
                {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day) => (
                  <div key={day} className="text-xs font-medium text-gray-500 text-center py-1">
                    {day}
                  </div>
                ))}
                
                {/* Calendar days */}
                {startCalendarDays.map((day, index) => {
                  if (day === null) {
                    return <div key={index} className="h-6" />;
                  }

                  const isFuture = isDateInFuture(startYear, startMonth, day);
                  const isSelected = isStartDateSelected(startYear, startMonth, day);
                  const isToday = startYear === new Date().getFullYear() && 
                                 startMonth === new Date().getMonth() && 
                                 day === new Date().getDate();

                  return (
                    <button
                      key={day}
                      onClick={() => !isFuture && handleStartDateClick(startYear, startMonth, day)}
                      disabled={isFuture}
                      className={`h-6 w-6 text-xs rounded transition-all duration-200 ${
                        isSelected
                          ? 'bg-blue-600 text-white font-medium'
                          : isToday
                          ? 'bg-gray-200 text-gray-900 font-medium'
                          : isFuture
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {day}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* End Date Calendar */}
        <div className="flex-1 bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="text-center mb-3">
            <h4 className="text-sm font-medium text-gray-700">End Date</h4>
          </div>
          
          <div className="flex space-x-2">
            {/* Year Selection */}
            <div className="w-16">
              <label className="block text-xs font-medium text-gray-600 mb-2">Year</label>
              <div className="space-y-1">
                {years.map((year) => (
                  <button
                    key={year}
                    onClick={() => setEndYear(year)}
                    className={`w-full px-2 py-1 text-xs rounded transition-colors ${
                      year === endYear
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {year}
                  </button>
                ))}
                {/* Custom Year Input */}
                <div className="pt-2 border-t border-gray-200">
                  <div className="relative">
                    <Edit3 className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-400" />
                    <input
                      type="number"
                      value={endYearInput}
                      onChange={(e) => {
                        setEndYearInput(e.target.value);
                        const year = parseInt(e.target.value);
                        const currentYear = new Date().getFullYear();
                        if (!isNaN(year) && year >= 2000 && year <= currentYear) {
                          setEndYear(year);
                        }
                      }}
                      onBlur={(e) => {
                        const year = parseInt(e.target.value);
                        const currentYear = new Date().getFullYear();
                        if (isNaN(year) || year < 2000 || year > currentYear) {
                          setEndYearInput(endYear.toString());
                        }
                      }}
                      placeholder="Year"
                      className={`w-full pl-6 pr-2 py-1 text-xs border rounded text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none ${
                        (() => {
                          const year = parseInt(endYearInput);
                          const currentYear = new Date().getFullYear();
                          return isNaN(year) || year < 2000 || year > currentYear
                            ? 'border-red-300 text-red-600 bg-red-50 focus:ring-red-500 focus:border-red-500'
                            : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500';
                        })()
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Month Selection */}
            <div className="w-20">
              <label className="block text-xs font-medium text-gray-600 mb-2">Month</label>
              <div className="grid grid-cols-2 gap-1">
                {months.map((month, index) => (
                  <button
                    key={month}
                    onClick={() => setEndMonth(index)}
                    className={`px-2 py-1 text-xs rounded transition-colors w-full ${
                      index === endMonth
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {month}
                  </button>
                ))}
              </div>
            </div>

            {/* Calendar Grid */}
            <div className="flex-1">
              <div className="grid grid-cols-7 gap-1">
                {/* Day headers */}
                {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day) => (
                  <div key={day} className="text-xs font-medium text-gray-500 text-center py-1">
                    {day}
                  </div>
                ))}
                
                {/* Calendar days */}
                {endCalendarDays.map((day, index) => {
                  if (day === null) {
                    return <div key={index} className="h-6" />;
                  }

                  const isFuture = isDateInFuture(endYear, endMonth, day);
                  const isSelected = isEndDateSelected(endYear, endMonth, day);
                  const isToday = endYear === new Date().getFullYear() && 
                                 endMonth === new Date().getMonth() && 
                                 day === new Date().getDate();

                  return (
                    <button
                      key={day}
                      onClick={() => !isFuture && handleEndDateClick(endYear, endMonth, day)}
                      disabled={isFuture}
                      className={`h-6 w-6 text-xs rounded transition-all duration-200 ${
                        isSelected
                          ? 'bg-blue-600 text-white font-medium'
                          : isToday
                          ? 'bg-gray-200 text-gray-900 font-medium'
                          : isFuture
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {day}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default CalendarSelector;
