import React, { useState } from 'react';
import { Settings, Eye, EyeOff, ChevronDown } from 'lucide-react';

export interface ColumnConfig {
  id: string;
  label: string;
  visible: boolean;
  category: 'basic' | 'returns' | 'risk' | 'dividends' | 'other';
}

interface ColumnVisibilityControlProps {
  columns: ColumnConfig[];
  onColumnToggle: (columnId: string) => void;
  onReset: () => void;
  onSelectAll: () => void;
  onClearAll: () => void;
  visibleCount: number;
  totalCount: number;
}

const ColumnVisibilityControl: React.FC<ColumnVisibilityControlProps> = ({
  columns,
  onColumnToggle,
  onReset,
  onSelectAll,
  onClearAll,
  visibleCount,
  totalCount
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const categories = {
    basic: { label: 'Basic Info', icon: '📊' },
    returns: { label: 'Returns', icon: '📈' },
    risk: { label: 'Risk Metrics', icon: '⚠️' },
    dividends: { label: 'Dividends', icon: '💰' },
    other: { label: 'Other', icon: '🔧' }
  };

  const groupedColumns = columns.reduce((acc, column) => {
    if (!acc[column.category]) {
      acc[column.category] = [];
    }
    acc[column.category].push(column);
    return acc;
  }, {} as Record<string, ColumnConfig[]>);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      >
        <Settings className="w-4 h-4" />
        <span>Columns</span>
        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
          {visibleCount}/{totalCount}
        </span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-900">Column Visibility</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={onSelectAll}
                  className="text-xs text-green-600 hover:text-green-700 font-medium"
                >
                  Select All
                </button>
                <button
                  onClick={onClearAll}
                  className="text-xs text-red-600 hover:text-red-700 font-medium"
                >
                  Clear All
                </button>
                <button
                  onClick={onReset}
                  className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                >
                  Reset
                </button>
              </div>
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {Object.entries(groupedColumns).map(([category, categoryColumns]) => (
                <div key={category}>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">{categories[category as keyof typeof categories]?.icon}</span>
                    <h4 className="text-sm font-medium text-gray-700">
                      {categories[category as keyof typeof categories]?.label}
                    </h4>
                  </div>
                  <div className="space-y-1 ml-6">
                    {categoryColumns.map((column) => (
                      <label
                        key={column.id}
                        className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
                      >
                        <input
                          type="checkbox"
                          checked={column.visible}
                          onChange={() => onColumnToggle(column.id)}
                          className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                        />
                        <span className="text-sm text-gray-700">{column.label}</span>
                        {column.visible ? (
                          <Eye className="w-3 h-3 text-green-500" />
                        ) : (
                          <EyeOff className="w-3 h-3 text-gray-400" />
                        )}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Showing {visibleCount} of {totalCount} columns</span>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ColumnVisibilityControl;
