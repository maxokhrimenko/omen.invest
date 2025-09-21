import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Upload, 
  BarChart3, 
  TrendingUp, 
  Settings, 
  Home
} from 'lucide-react';
import Logo from '../Logo';

interface SidebarProps {
  isCollapsed?: boolean;
  onToggle?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed = false }) => {
  const location = useLocation();

  const menuItems = [
    {
      path: '/',
      label: 'Dashboard',
      icon: Home,
      description: 'Overview and quick stats'
    },
    {
      path: '/portfolio/upload',
      label: 'Portfolio Upload',
      icon: Upload,
      description: 'Upload and manage portfolio'
    },
    {
      path: '/portfolio/analysis',
      label: 'Portfolio Analysis',
      icon: BarChart3,
      description: 'Analyze portfolio performance'
    },
    {
      path: '/tickers/analysis',
      label: 'Ticker Analysis',
      icon: TrendingUp,
      description: 'Individual ticker analysis'
    },
    {
      path: '/settings',
      label: 'Settings',
      icon: Settings,
      description: 'Application settings'
    }
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className={`bg-white border-r border-gray-200 transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-72'
    }`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center overflow-hidden">
            <Logo />
          </div>
          {!isCollapsed && (
            <div>
              <h1 className="text-xl font-bold text-gray-900">Omen Screen</h1>
              <p className="text-sm text-gray-500">Deep portfolio analysis</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors group ${
                active
                  ? 'bg-primary-50 text-primary-700 border border-primary-200'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 ${
                active ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'
              }`} />
              {!isCollapsed && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.label}</p>
                  <p className="text-xs text-gray-500 truncate">{item.description}</p>
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            <p>Portfolio Analysis Tool</p>
            <p>v1.0.0</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
