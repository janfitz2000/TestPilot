import React, { useState } from 'react';
import { Play, CheckCircle, XCircle, Clock, Plus, Eye, Download, Settings } from 'lucide-react';
import TestRecorder from '../components/TestRecorder';
import ChatInterface from '../components/ChatInterface';

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
  const [activeView, setActiveView] = useState<'list' | 'recorder' | 'ai'>('list');

  if (activeView === 'recorder') {
    return (
      <div className="h-screen flex flex-col">
        <div className="flex-shrink-0 border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setActiveView('list')}
              className="text-blue-600 hover:text-blue-800"
            >
              ← Back to Tests
            </button>
            <h1 className="text-xl font-bold text-gray-900">Test Recorder & Real-time Plotter</h1>
            <div className="w-20"></div>
          </div>
        </div>
        <div className="flex-1">
          <TestRecorder />
        </div>
      </div>
    );
  }

  if (activeView === 'ai') {
    return (
      <div className="h-screen flex flex-col">
        <div className="flex-shrink-0 border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setActiveView('list')}
              className="text-blue-600 hover:text-blue-800"
            >
              ← Back to Tests
            </button>
            <h1 className="text-xl font-bold text-gray-900">AI Test Assistant</h1>
            <div className="w-20"></div>
          </div>
        </div>
        <div className="flex-1">
          <ChatInterface />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Test Management</h1>
          <p className="mt-2 text-gray-600">Execute tests with AI assistance and real-time recording</p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={() => setActiveView('ai')}
            className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            <Settings className="w-4 h-4 mr-2" />
            AI Assistant
          </button>
          <button
            onClick={() => setActiveView('recorder')}
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Play className="w-4 h-4 mr-2" />
            Start Recording
          </button>
        </div>
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
                  
                  <button 
                    onClick={() => setActiveView('recorder')}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Info Panels */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Real-time Recording</h3>
          <p className="text-sm opacity-90 mb-4">Record measurements with live plotting and data export</p>
          <button 
            onClick={() => setActiveView('recorder')}
            className="bg-white text-blue-600 px-4 py-2 rounded font-medium hover:bg-blue-50"
          >
            Start Recording
          </button>
        </div>
        
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">AI Test Assistant</h3>
          <p className="text-sm opacity-90 mb-4">Generate test plans and analyze results with AI</p>
          <button 
            onClick={() => setActiveView('ai')}
            className="bg-white text-purple-600 px-4 py-2 rounded font-medium hover:bg-purple-50"
          >
            Open AI Chat
          </button>
        </div>
        
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Data Output Format</h3>
          <p className="text-sm opacity-90 mb-4">Export data in JSON, CSV, or custom formats for LLM consumption</p>
          <button className="bg-white text-green-600 px-4 py-2 rounded font-medium hover:bg-green-50">
            Configure Format
          </button>
        </div>
      </div>
    </div>
  );
}