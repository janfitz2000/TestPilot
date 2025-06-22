import React from 'react';
import { Activity, Cpu, GitBranch, AlertCircle } from 'lucide-react';
import ChatInterface from '../components/ChatInterface';

const stats = [
  { name: 'Active Instruments', value: '12', icon: Cpu, color: 'text-blue-600' },
  { name: 'Running Tests', value: '3', icon: Activity, color: 'text-green-600' },
  { name: 'Active Workflows', value: '8', icon: GitBranch, color: 'text-purple-600' },
  { name: 'Alerts', value: '2', icon: AlertCircle, color: 'text-red-600' },
];

const recentTests = [
  { id: 1, name: 'Power Amplifier Test', status: 'Running', progress: 65 },
  { id: 2, name: 'Oscilloscope Calibration', status: 'Completed', progress: 100 },
  { id: 3, name: 'Signal Generator Sweep', status: 'Queued', progress: 0 },
];

export default function Dashboard() {
  return (
    <div className="flex h-full">
      {/* Left Panel - Dashboard Stats */}
      <div className="w-1/3 p-6 border-r border-gray-200">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            AI-driven test automation platform
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-4 mb-6">
          {stats.map((stat) => (
            <div key={stat.name} className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-3">
                  <div className="text-lg font-bold text-gray-900">{stat.value}</div>
                  <div className="text-xs text-gray-500">{stat.name}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent Tests */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-4 py-3 border-b border-gray-200">
            <h2 className="text-sm font-medium text-gray-900">Recent Tests</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {recentTests.map((test) => (
              <div key={test.id} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs font-medium text-gray-900">{test.name}</div>
                    <div className="text-xs text-gray-500">{test.status}</div>
                  </div>
                  <div className="text-xs text-gray-500">{test.progress}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Panel - AI Chat Interface */}
      <div className="flex-1">
        <ChatInterface />
      </div>
    </div>
  );
}