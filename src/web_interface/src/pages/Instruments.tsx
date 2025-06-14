import React, { useState } from 'react';
import { Plus, Cpu, Wifi, WifiOff } from 'lucide-react';

const mockInstruments = [
  { id: 1, name: 'Keysight MSO-X 3104T', type: 'Oscilloscope', address: '192.168.1.100', connected: true },
  { id: 2, name: 'Rigol DG4162', type: 'Signal Generator', address: '192.168.1.101', connected: true },
  { id: 3, name: 'Keysight B2900A', type: 'SMU', address: '192.168.1.102', connected: false },
  { id: 4, name: 'R&S FSW', type: 'Spectrum Analyzer', address: '192.168.1.103', connected: true },
];

export default function Instruments() {
  const [instruments, setInstruments] = useState(mockInstruments);
  const [showAddModal, setShowAddModal] = useState(false);

  const toggleConnection = (id: number) => {
    setInstruments(instruments.map(inst => 
      inst.id === id ? { ...inst, connected: !inst.connected } : inst
    ));
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Instruments</h1>
          <p className="mt-2 text-gray-600">Manage your test instruments</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Instrument
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {instruments.map((instrument) => (
          <div key={instrument.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <Cpu className="w-8 h-8 text-gray-600" />
              {instrument.connected ? (
                <Wifi className="w-6 h-6 text-green-500" />
              ) : (
                <WifiOff className="w-6 h-6 text-red-500" />
              )}
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {instrument.name}
            </h3>
            
            <div className="space-y-2 mb-4">
              <div className="text-sm">
                <span className="text-gray-500">Type:</span>
                <span className="ml-2 text-gray-900">{instrument.type}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-500">Address:</span>
                <span className="ml-2 text-gray-900">{instrument.address}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-500">Status:</span>
                <span className={`ml-2 ${instrument.connected ? 'text-green-600' : 'text-red-600'}`}>
                  {instrument.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => toggleConnection(instrument.id)}
                className={`flex-1 px-3 py-2 rounded text-sm font-medium ${
                  instrument.connected
                    ? 'bg-red-100 text-red-700 hover:bg-red-200'
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                {instrument.connected ? 'Disconnect' : 'Connect'}
              </button>
              <button className="px-3 py-2 bg-gray-100 text-gray-700 rounded text-sm font-medium hover:bg-gray-200">
                Configure
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}