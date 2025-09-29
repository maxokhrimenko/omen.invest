import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Upload, BarChart3, TrendingUp, Settings, GitCompare } from 'lucide-react';
import Logo from '../Logo';
import type { Portfolio } from '../../types/portfolio';

interface SidebarProps {
  portfolio: Portfolio | null;
}

const Sidebar: React.FC<SidebarProps> = ({ portfolio }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const getBadgeClasses = (badge: { text: string; color: string }) => {
    const baseClasses = 'inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium whitespace-nowrap min-w-fit';
    switch (badge.color) {
      case 'red':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'purple':
        return `${baseClasses} bg-purple-100 text-purple-800`;
      case 'blue':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'green':
        return `${baseClasses} bg-green-100 text-green-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const menuGroups = [
    {
      title: 'PORTFOLIO',
      items: [
        {
          path: '/',
          label: 'Portfolio Management',
          icon: Upload,
          badge: null,
          disabled: false
        }
      ]
    },
    {
      title: 'ANALYSIS',
      items: [
        {
          path: '/portfolio/analysis',
          label: 'Portfolio Analysis',
          icon: BarChart3,
          badge: { text: 'new', color: 'red' },
          disabled: !portfolio
        },
        {
          path: '/tickers/analysis',
          label: 'Tickers Analysis',
          icon: TrendingUp,
          badge: { text: 'new', color: 'red' },
          disabled: !portfolio
        },
        {
          path: '/tickers/compare',
          label: 'Compare Tickers',
          icon: GitCompare,
          badge: { text: 'new', color: 'red' },
          disabled: !portfolio
        }
      ]
    }
  ];

  const adminItem = {
    path: '/administration',
    label: 'Administration',
    icon: Settings,
    badge: null as { text: string; color: string } | null,
    disabled: false
  };

  return (
    <div className="w-72 bg-white border-r border-gray-200 h-screen flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 flex items-center justify-center">
            <Logo />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900 leading-tight">
              Altidus
            </h1>
            <p className="text-sm text-gray-500 mt-1">Charts rise,<br />charts may fall</p>
            <div className="mt-2">
              <span className="inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 whitespace-nowrap">
                alpha 4.5.3
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <nav className="p-4 space-y-6 flex-1">
        {menuGroups.map((group) => (
          <div key={group.title} className="space-y-2">
            {/* Group Header */}
            <div className="px-3 py-2">
              <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                {group.title}
              </h3>
            </div>
            
            {/* Group Items */}
            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);
                const isDisabled = item.disabled;
                
                const menuItem = (
                  <div
                    className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                      isDisabled
                        ? 'text-gray-400 cursor-not-allowed opacity-50'
                        : active
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className={`w-5 h-5 mr-3 ${
                      isDisabled 
                        ? 'text-gray-400' 
                        : active 
                        ? 'text-blue-600' 
                        : 'text-gray-400'
                    }`} />
                    <div className="flex-1 flex items-center justify-between min-w-0">
                      <span className="font-medium truncate">{item.label}</span>
                      {item.badge && (
                        <span className={`${getBadgeClasses(item.badge)} ml-2 flex-shrink-0`}>
                          {item.badge.text}
                        </span>
                      )}
                    </div>
                  </div>
                );
                
                if (isDisabled) {
                  return (
                    <div key={item.path} onClick={(e) => e.preventDefault()}>
                      {menuItem}
                    </div>
                  );
                }
                
                return (
                  <Link key={item.path} to={item.path}>
                    {menuItem}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Administration Section */}
      <div className="p-4 border-t border-gray-200">
        <div className="space-y-1">
          {(() => {
            const Icon = adminItem.icon;
            const active = isActive(adminItem.path);
            const isDisabled = adminItem.disabled;
            
            const menuItem = (
              <div
                className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                  isDisabled
                    ? 'text-gray-400 cursor-not-allowed opacity-50'
                    : active
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon className={`w-5 h-5 mr-3 ${
                  isDisabled 
                    ? 'text-gray-400' 
                    : active 
                    ? 'text-blue-600' 
                    : 'text-gray-400'
                }`} />
                <div className="flex-1 flex items-center justify-between min-w-0">
                  <span className="font-medium truncate">{adminItem.label}</span>
                  {adminItem.badge && (
                    <span className={`${getBadgeClasses(adminItem.badge)} ml-2 flex-shrink-0`}>
                      {adminItem.badge.text}
                    </span>
                  )}
                </div>
              </div>
            );
            
            if (isDisabled) {
              return (
                <div onClick={(e) => e.preventDefault()}>
                  {menuItem}
                </div>
              );
            }
            
            return (
              <Link to={adminItem.path}>
                {menuItem}
              </Link>
            );
          })()}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
