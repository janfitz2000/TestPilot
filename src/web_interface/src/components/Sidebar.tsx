import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Cpu, 
  GitBranch, 
  Play, 
  Settings,
  Activity
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Instruments', href: '/instruments', icon: Cpu },
  { name: 'Workflows', href: '/workflows', icon: GitBranch },
  { name: 'Tests', href: '/tests', icon: Play },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <div className="flex flex-col w-64 bg-gray-800">
      <div className="flex items-center h-16 px-4 bg-gray-900">
        <Activity className="w-8 h-8 text-blue-500" />
        <span className="ml-2 text-xl font-bold text-white">TestPilot</span>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`${
                isActive
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              } group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors`}
            >
              <item.icon
                className={`${
                  isActive ? 'text-gray-300' : 'text-gray-400 group-hover:text-gray-300'
                } mr-3 flex-shrink-0 w-6 h-6`}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}