import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Square, Download, Settings, BarChart3 } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface MeasurementData {
  timestamp: number;
  frequency: number;
  amplitude: number;
  phase: number;
  power: number;
}

interface TestSession {
  id: string;
  name: string;
  startTime: Date;
  endTime?: Date;
  status: 'idle' | 'recording' | 'paused' | 'completed';
  measurements: MeasurementData[];
  metadata: {
    instruments: string[];
    testType: string;
    sampleRate: number;
  };
}

const TestRecorder: React.FC = () => {
  const [currentSession, setCurrentSession] = useState<TestSession | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [measurements, setMeasurements] = useState<MeasurementData[]>([]);
  const [plotType, setPlotType] = useState<'amplitude' | 'phase' | 'power'>('amplitude');
  const [sampleRate, setSampleRate] = useState(10); // Hz
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize new test session
  const startNewSession = () => {
    const newSession: TestSession = {
      id: `test_${Date.now()}`,
      name: `Test Session ${new Date().toLocaleString()}`,
      startTime: new Date(),
      status: 'idle',
      measurements: [],
      metadata: {
        instruments: ['Signal Generator', 'Spectrum Analyzer', 'Power Meter'],
        testType: 'RF Characterization',
        sampleRate: sampleRate
      }
    };
    setCurrentSession(newSession);
    setMeasurements([]);
  };

  // Start recording measurements
  const startRecording = () => {
    if (!currentSession) {
      startNewSession();
      return;
    }

    setIsRecording(true);
    setCurrentSession(prev => prev ? { ...prev, status: 'recording' } : null);

    // Simulate real-time measurements
    intervalRef.current = setInterval(() => {
      const timestamp = Date.now();
      const newMeasurement: MeasurementData = {
        timestamp,
        frequency: 2.4e9 + Math.random() * 0.1e9, // 2.4-2.5 GHz
        amplitude: 20 + Math.random() * 5 - 2.5, // 17.5 to 22.5 dBm
        phase: Math.random() * 360 - 180, // -180 to +180 degrees
        power: 15 + Math.random() * 10 - 5 // 10 to 20 dBm
      };

      setMeasurements(prev => [...prev, newMeasurement]);
      
      // Update session
      setCurrentSession(prev => 
        prev ? { 
          ...prev, 
          measurements: [...prev.measurements, newMeasurement] 
        } : null
      );
    }, 1000 / sampleRate);
  };

  // Pause recording
  const pauseRecording = () => {
    setIsRecording(false);
    setCurrentSession(prev => prev ? { ...prev, status: 'paused' } : null);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  // Stop recording
  const stopRecording = () => {
    setIsRecording(false);
    setCurrentSession(prev => 
      prev ? { 
        ...prev, 
        status: 'completed',
        endTime: new Date()
      } : null
    );
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  // Export data
  const exportData = () => {
    if (!currentSession) return;

    const exportData = {
      session: currentSession,
      measurements: measurements,
      exportTime: new Date().toISOString(),
      format: 'TestPilot Data Export v1.0'
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${currentSession.id}_data.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Prepare chart data
  const getChartData = () => {
    const labels = measurements.map((_, index) => index);
    let dataValues: number[] = [];
    let label = '';
    let color = '';

    switch (plotType) {
      case 'amplitude':
        dataValues = measurements.map(m => m.amplitude);
        label = 'Amplitude (dBm)';
        color = 'rgb(59, 130, 246)';
        break;
      case 'phase':
        dataValues = measurements.map(m => m.phase);
        label = 'Phase (degrees)';
        color = 'rgb(16, 185, 129)';
        break;
      case 'power':
        dataValues = measurements.map(m => m.power);
        label = 'Power (dBm)';
        color = 'rgb(245, 101, 101)';
        break;
    }

    return {
      labels,
      datasets: [
        {
          label,
          data: dataValues,
          borderColor: color,
          backgroundColor: color + '20',
          tension: 0.1,
          pointRadius: 1,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `Real-time ${plotType.charAt(0).toUpperCase() + plotType.slice(1)} Measurements`,
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Sample Number',
        },
      },
      y: {
        display: true,
        title: {
          display: true,
          text: plotType === 'phase' ? 'Degrees' : 'dBm',
        },
      },
    },
    animation: {
      duration: 0 // Disable animations for real-time data
    }
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Test Recorder</h2>
            <p className="text-sm text-gray-500">
              {currentSession ? currentSession.name : 'No active session'}
            </p>
          </div>
          
          {/* Recording Controls */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1 mr-4">
              <Settings className="w-4 h-4 text-gray-400" />
              <select 
                value={sampleRate} 
                onChange={(e) => setSampleRate(Number(e.target.value))}
                className="text-sm border rounded px-2 py-1"
                disabled={isRecording}
              >
                <option value={1}>1 Hz</option>
                <option value={5}>5 Hz</option>
                <option value={10}>10 Hz</option>
                <option value={20}>20 Hz</option>
                <option value={50}>50 Hz</option>
              </select>
            </div>

            {!isRecording ? (
              <button
                onClick={startRecording}
                className="flex items-center px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Play className="w-4 h-4 mr-1" />
                Start
              </button>
            ) : (
              <button
                onClick={pauseRecording}
                className="flex items-center px-3 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
              >
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </button>
            )}

            <button
              onClick={stopRecording}
              className="flex items-center px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              disabled={!currentSession}
            >
              <Square className="w-4 h-4 mr-1" />
              Stop
            </button>

            <button
              onClick={exportData}
              className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              disabled={!currentSession || measurements.length === 0}
            >
              <Download className="w-4 h-4 mr-1" />
              Export
            </button>
          </div>
        </div>

        {/* Session Status */}
        {currentSession && (
          <div className="mt-3 flex items-center space-x-4 text-sm text-gray-600">
            <span>Status: 
              <span className={`ml-1 font-medium ${
                currentSession.status === 'recording' ? 'text-green-600' : 
                currentSession.status === 'paused' ? 'text-yellow-600' :
                currentSession.status === 'completed' ? 'text-blue-600' : 'text-gray-600'
              }`}>
                {currentSession.status.toUpperCase()}
              </span>
            </span>
            <span>Samples: {measurements.length}</span>
            <span>Duration: {
              currentSession.endTime 
                ? Math.round((currentSession.endTime.getTime() - currentSession.startTime.getTime()) / 1000)
                : Math.round((Date.now() - currentSession.startTime.getTime()) / 1000)
            }s</span>
          </div>
        )}
      </div>

      {/* Plot Controls */}
      <div className="flex-shrink-0 border-b border-gray-200 p-3">
        <div className="flex items-center space-x-4">
          <BarChart3 className="w-5 h-5 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Plot Type:</span>
          <div className="flex space-x-2">
            {(['amplitude', 'phase', 'power'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setPlotType(type)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  plotType === type
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Real-time Plot */}
      <div className="flex-1 p-4">
        {measurements.length > 0 ? (
          <div className="h-full">
            <Line data={getChartData()} options={chartOptions} />
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No Data Recorded</p>
              <p className="text-sm">Start recording to see real-time measurements</p>
            </div>
          </div>
        )}
      </div>

      {/* Data Table */}
      {measurements.length > 0 && (
        <div className="flex-shrink-0 border-t border-gray-200 p-4 max-h-48 overflow-y-auto">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Recent Measurements</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-2 py-1 text-left">Time</th>
                  <th className="px-2 py-1 text-left">Frequency (GHz)</th>
                  <th className="px-2 py-1 text-left">Amplitude (dBm)</th>
                  <th className="px-2 py-1 text-left">Phase (°)</th>
                  <th className="px-2 py-1 text-left">Power (dBm)</th>
                </tr>
              </thead>
              <tbody>
                {measurements.slice(-10).reverse().map((measurement, index) => (
                  <tr key={index} className="border-t border-gray-100">
                    <td className="px-2 py-1">{new Date(measurement.timestamp).toLocaleTimeString()}</td>
                    <td className="px-2 py-1">{(measurement.frequency / 1e9).toFixed(3)}</td>
                    <td className="px-2 py-1">{measurement.amplitude.toFixed(2)}</td>
                    <td className="px-2 py-1">{measurement.phase.toFixed(1)}</td>
                    <td className="px-2 py-1">{measurement.power.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestRecorder;