import React from 'react';
import { Plus, GitBranch, Play, Edit } from 'lucide-react';

const mockWorkflows = [
  { id: 1, name: 'Power Amplifier Characterization', description: 'Complete PA testing workflow', steps: 12, lastRun: '2 hours ago' },
  { id: 2, name: 'Oscilloscope Calibration', description: 'Automated calibration procedure', steps: 8, lastRun: '1 day ago' },
  { id: 3, name: 'Filter Response Analysis', description: 'Frequency response measurement', steps: 15, lastRun: '3 days ago' },
];

export default function Workflows() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="mt-2 text-gray-600">Create and manage test workflows</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Create Workflow
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockWorkflows.map((workflow) => (
          <div key={workflow.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <GitBranch className="w-8 h-8 text-purple-600" />
              <span className="text-sm text-gray-500">{workflow.steps} steps</span>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {workflow.name}
            </h3>
            
            <p className="text-gray-600 text-sm mb-4">
              {workflow.description}
            </p>
            
            <div className="text-xs text-gray-500 mb-4">
              Last run: {workflow.lastRun}
            </div>
            
            <div className="flex space-x-2">
              <button className="flex-1 bg-green-600 text-white px-3 py-2 rounded text-sm font-medium hover:bg-green-700 flex items-center justify-center">
                <Play className="w-4 h-4 mr-1" />
                Run
              </button>
              <button className="px-3 py-2 bg-gray-100 text-gray-700 rounded text-sm font-medium hover:bg-gray-200">
                <Edit className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}