import React from 'react';
import { Activity, Cpu, GitBranch, AlertCircle } from 'lucide-react';

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
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to TestPilot - AI-driven test automation platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-sm text-gray-500">{stat.name}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Tests */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Tests</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentTests.map((test) => (
            <div key={test.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-900">{test.name}</div>
                  <div className="text-sm text-gray-500">Status: {test.status}</div>
                </div>
                <div className="flex items-center">
                  <div className="text-sm text-gray-500 mr-4">{test.progress}%</div>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${test.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}