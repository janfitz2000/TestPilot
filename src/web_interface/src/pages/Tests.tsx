import React from 'react';
import { Play, CheckCircle, XCircle, Clock } from 'lucide-react';

const mockTests = [
  { id: 1, name: 'Power Amplifier Test', status: 'running', progress: 65, startTime: '10:30 AM', duration: '15 min' },
  { id: 2, name: 'Oscilloscope Calibration', status: 'completed', progress: 100, startTime: '9:45 AM', duration: '8 min' },
  { id: 3, name: 'Signal Generator Sweep', status: 'queued', progress: 0, startTime: 'Pending', duration: '-' },
  { id: 4, name: 'Filter Response Test', status: 'failed', progress: 45, startTime: '8:15 AM', duration: '12 min' },
];

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'running':
      return <Clock className="w-5 h-5 text-blue-500" />;
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'failed':
      return <XCircle className="w-5 h-5 text-red-500" />;
    case 'queued':
      return <Clock className="w-5 h-5 text-gray-500" />;
    default:
      return <Clock className="w-5 h-5 text-gray-500" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'running':
      return 'text-blue-600 bg-blue-100';
    case 'completed':
      return 'text-green-600 bg-green-100';
    case 'failed':
      return 'text-red-600 bg-red-100';
    case 'queued':
      return 'text-gray-600 bg-gray-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};

export default function Tests() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Test Executions</h1>
          <p className="mt-2 text-gray-600">Monitor and manage test executions</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
          <Play className="w-4 h-4 mr-2" />
          Run Test
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Active Tests</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {mockTests.map((test) => (
            <div key={test.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(test.status)}
                  <div>
                    <div className="text-sm font-medium text-gray-900">{test.name}</div>
                    <div className="text-sm text-gray-500">
                      Started: {test.startTime} • Duration: {test.duration}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(test.status)}`}>
                    {test.status.charAt(0).toUpperCase() + test.status.slice(1)}
                  </span>
                  
                  <div className="flex items-center space-x-2">
                    <div className="text-sm text-gray-500">{test.progress}%</div>
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          test.status === 'completed' ? 'bg-green-500' :
                          test.status === 'failed' ? 'bg-red-500' :
                          test.status === 'running' ? 'bg-blue-500' : 'bg-gray-400'
                        }`}
                        style={{ width: `${test.progress}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <button className="text-gray-400 hover:text-gray-600">
                    <Play className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}