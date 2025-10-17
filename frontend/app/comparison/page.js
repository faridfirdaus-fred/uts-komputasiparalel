'use client';

import { useState } from 'react';
import Link from 'next/link';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE = 'http://localhost:8000';

export default function ComparisonPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [analysisType, setAnalysisType] = useState('thread-process');

  // Preset configurations untuk benchmark
  const threadPresets = [
    { name: '2 Threads', io_workers: 2, cpu_workers: 2, limit_data: 500 },
    { name: '4 Threads', io_workers: 4, cpu_workers: 2, limit_data: 500 },
    { name: '8 Threads', io_workers: 8, cpu_workers: 2, limit_data: 500 },
    { name: '12 Threads', io_workers: 12, cpu_workers: 2, limit_data: 500 },
    { name: '16 Threads', io_workers: 16, cpu_workers: 2, limit_data: 500 },
  ];

  const processPresets = [
    { name: '2 Processes', io_workers: 4, cpu_workers: 2, limit_data: 500 },
    { name: '4 Processes', io_workers: 4, cpu_workers: 4, limit_data: 500 },
    { name: '8 Processes', io_workers: 4, cpu_workers: 8, limit_data: 500 },
    { name: '12 Processes', io_workers: 4, cpu_workers: 12, limit_data: 500 },
    { name: '16 Processes', io_workers: 4, cpu_workers: 16, limit_data: 500 },
  ];

  const mpiPresets = [
    { name: '2 Ranks', mpi_ranks: 2, io_workers: 4, cpu_workers: 4, limit_data: 500 },
    { name: '4 Ranks', mpi_ranks: 4, io_workers: 4, cpu_workers: 4, limit_data: 500 },
    { name: '8 Ranks', mpi_ranks: 8, io_workers: 4, cpu_workers: 4, limit_data: 500 },
  ];

  const runBenchmark = async () => {
    setLoading(true);
    setResults([]);
    
    let presets;
    let endpoint;
    
    if (analysisType === 'thread-process') {
      presets = threadPresets;
      endpoint = '/api/analyze/thread-process';
    } else if (analysisType === 'process') {
      presets = processPresets;
      endpoint = '/api/analyze/thread-process';
    } else {
      presets = mpiPresets;
      endpoint = '/api/analyze/mpi';
    }

    const benchmarkResults = [];

    for (const preset of presets) {
      try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...preset, detailed: true }),
        });

        if (response.ok) {
          const data = await response.json();
          benchmarkResults.push({
            name: preset.name,
            time: data.execution_time || 0,
            speedup: data.stats?.speedup || 0,
            efficiency: (data.stats?.efficiency || 0) * 100,
            throughput: data.stats?.throughput || 0,
            config: analysisType === 'mpi' 
              ? `${preset.mpi_ranks}r/${preset.io_workers}io/${preset.cpu_workers}cpu`
              : `${preset.io_workers}io/${preset.cpu_workers}cpu`,
          });
        }
      } catch (error) {
        console.error(`Error running ${preset.name}:`, error);
      }
    }

    setResults(benchmarkResults);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          📊 Performance Comparison
        </h1>
        <Link href="/" className="text-blue-600 hover:text-blue-800 font-medium">
          ← Back to Home
        </Link>
      </div>

      {/* Control Panel */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Benchmark Configuration</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Type
            </label>
            <select
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            >
              <option value="thread-process">Thread Scalability (I/O Workers)</option>
              <option value="process">Process Scalability (CPU Workers)</option>
              <option value="mpi">MPI Ranks Scalability</option>
            </select>
          </div>

          <button
            onClick={runBenchmark}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Running Benchmark...' : 'Start Benchmark'}
          </button>

          {loading && (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-sm text-gray-600 mt-2">
                Running multiple configurations... This may take a few minutes.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      {results.length > 0 && (
        <div className="space-y-6">
          {/* Time vs Configuration Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Execution Time vs Configuration
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={results}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: 'Time (seconds)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="time" stroke="#3b82f6" strokeWidth={2} name="Execution Time" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Speedup Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Speedup vs Configuration
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={results}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: 'Speedup (x)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="speedup" fill="#10b981" name="Speedup" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Efficiency Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Efficiency vs Configuration
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={results}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: 'Efficiency (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="efficiency" fill="#f59e0b" name="Efficiency %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Throughput Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Throughput vs Configuration
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={results}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: 'Files/Second', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="throughput" stroke="#8b5cf6" strokeWidth={2} name="Throughput" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Results Table */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Detailed Results
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Configuration
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time (s)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Speedup
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Efficiency (%)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Throughput
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.map((result, idx) => (
                    <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {result.name}
                        <br />
                        <span className="text-xs text-gray-500">{result.config}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.time.toFixed(3)}s
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.speedup.toFixed(2)}x
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.efficiency.toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.throughput.toFixed(2)} files/s
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {!loading && results.length === 0 && (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <p className="text-lg text-gray-500">
            Select a benchmark type and click &quot;Start Benchmark&quot; to begin performance comparison.
          </p>
        </div>
      )}
    </div>
  );
}
