import React from 'react';
import { Table, Grid3X3 } from 'lucide-react';

interface ViewToggleProps {
  viewMode: 'table' | 'cards';
  setViewMode: (mode: 'table' | 'cards') => void;
  disabled?: boolean;
}

const ViewToggle: React.FC<ViewToggleProps> = ({ viewMode, setViewMode, disabled = false }) => {
  return (
    <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
      <button
        onClick={() => setViewMode('cards')}
        disabled={disabled}
        className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          viewMode === 'cards'
            ? 'bg-white text-primary-700 shadow-sm'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <Grid3X3 className="w-4 h-4" />
        <span>Cards</span>
      </button>
      <button
        onClick={() => setViewMode('table')}
        disabled={disabled}
        className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          viewMode === 'table'
            ? 'bg-white text-primary-700 shadow-sm'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <Table className="w-4 h-4" />
        <span>Table</span>
      </button>
    </div>
  );
};

export default ViewToggle;
