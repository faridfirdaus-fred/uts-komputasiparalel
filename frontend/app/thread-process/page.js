'use client';

import { useState } from 'react';
import Link from 'next/link';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE = 'http://localhost:8000';

export default function ThreadProcessPage() {
  const [config, setConfig] = useState({
    io_workers: 3,
    cpu_workers: 2,
    limit_data: 810,
    detailed: true,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/api/analyze/thread-process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
      
      // Add to history for chart
      const historyEntry = {
        name: `${config.io_workers}io/${config.cpu_workers}cpu/${config.limit_data}f`,
        time: data.execution_time || 0,
        speedup: data.stats?.speedup || 0,
        efficiency: (data.stats?.efficiency || 0) * 100,
        throughput: data.stats?.throughput || 0,
        timestamp: new Date().toLocaleTimeString(),
      };
      setHistory(prev => [...prev, historyEntry]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const presets = [
    { name: '1. Baseline (NIM 237006081)', io_workers: 3, cpu_workers: 2, limit_data: 810 },
    { name: '2. Light (2/2)', io_workers: 2, cpu_workers: 2, limit_data: 810 },
    { name: '3. Medium (4/4)', io_workers: 4, cpu_workers: 4, limit_data: 810 },
    { name: '4. Balanced (8/8)', io_workers: 8, cpu_workers: 8, limit_data: 810 },
    { name: '5. I/O Heavy (16/4)', io_workers: 16, cpu_workers: 4, limit_data: 810 },
    { name: '6. CPU Heavy (4/16)', io_workers: 4, cpu_workers: 16, limit_data: 810 },
    { name: '7. High Parallelism (12/12)', io_workers: 12, cpu_workers: 12, limit_data: 810 },
    { name: '8. Test 500 files (6/6)', io_workers: 6, cpu_workers: 6, limit_data: 500 },
    { name: '9. Test 200 files (4/4)', io_workers: 4, cpu_workers: 4, limit_data: 200 },
    { name: '10. Quick Test 100 files', io_workers: 2, cpu_workers: 2, limit_data: 100 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-100">
          ⚡ Thread + ProcessPool Analysis
        </h1>
        <div className="flex items-center space-x-4">
          <Link
            href="/comparison"
            className="text-gray-600 hover:text-gray-900 font-medium"
          >
            📊 Comparison
          </Link>
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Home
          </Link>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Configuration Form */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Configuration</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  I/O Threads
                </label>
                <input
                  type="number"
                  min="1"
                  max="32"
                  value={config.io_workers}
                  onChange={(e) =>
                    setConfig({ ...config, io_workers: parseInt(e.target.value) })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Number of threads for I/O operations (1-32)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CPU Processes
                </label>
                <input
                  type="number"
                  min="1"
                  max="32"
                  value={config.cpu_workers}
                  onChange={(e) =>
                    setConfig({ ...config, cpu_workers: parseInt(e.target.value) })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Number of processes for CPU tasks (1-32)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Files to Process
                </label>
                <input
                  type="number"
                  min="1"
                  max="810"
                  value={config.limit_data}
                  onChange={(e) =>
                    setConfig({ ...config, limit_data: parseInt(e.target.value) })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Maximum: 810 files
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.detailed}
                  onChange={(e) =>
                    setConfig({ ...config, detailed: e.target.checked })
                  }
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Detailed Analysis
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Running Analysis...' : 'Start Analysis'}
              </button>
            </form>

            {/* Presets */}
            <div className="mt-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Quick Presets:</h3>
              <div className="space-y-2">
                {presets.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() =>
                      setConfig({
                        ...config,
                        io_workers: preset.io_workers,
                        cpu_workers: preset.cpu_workers,
                        limit_data: preset.limit_data,
                      })
                    }
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    {preset.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Results</h2>

            {loading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-gray-600">Running analysis... This may take a moment.</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-red-800 font-semibold">Error:</p>
                <p className="text-red-600">{error}</p>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                {/* Metrics Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                    <p className="text-sm text-blue-700 font-semibold">Speedup</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {result.stats?.speedup?.toFixed(2)}x
                    </p>
                  </div>
                  <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                    <p className="text-sm text-green-700 font-semibold">Efficiency</p>
                    <p className="text-2xl font-bold text-green-900">
                      {((result.stats?.efficiency || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                    <p className="text-sm text-purple-700 font-semibold">Throughput</p>
                    <p className="text-2xl font-bold text-purple-900">
                      {result.stats?.throughput?.toFixed(0)} files/s
                    </p>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 p-4 rounded-lg">
                    <p className="text-sm text-orange-700 font-semibold">Time</p>
                    <p className="text-2xl font-bold text-orange-900">
                      {result.execution_time?.toFixed(2)}s
                    </p>
                  </div>
                </div>

                {/* Detailed Stats */}
                {result.stats && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Statistics</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Files Processed:</span>
                        <span className="font-semibold text-gray-900 ml-2">
                          {result.stats.files_processed || config.limit_data}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Total Words:</span>
                        <span className="font-semibold text-gray-900 ml-2">
                          {result.stats.total_words?.toLocaleString() || 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Sequential Time:</span>
                        <span className="font-semibold text-gray-900 ml-2">
                          {result.stats.sequential_time?.toFixed(3)}s
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Parallel Time:</span>
                        <span className="font-semibold text-gray-900 ml-2">
                          {result.stats.parallel_time?.toFixed(3)}s
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Output Log */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Full Output:</h3>
                  <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-xs overflow-auto max-h-96">
                    <pre>{result.output}</pre>
                  </div>
                </div>
              </div>
            )}

            {!loading && !error && !result && (
              <div className="text-center py-12 text-gray-500">
                <p className="text-lg">Configure your analysis and click &quot;Start Analysis&quot; to begin.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Charts Section - Shows history of runs */}
      {history.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Performance History ({history.length} runs)</h2>
            <button
              onClick={() => setHistory([])}
              className="text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Clear History
            </button>
          </div>

          <div className="space-y-6">
            {/* Execution Time Chart */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Execution Time</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis label={{ value: 'Time (s)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="time" stroke="#3b82f6" strokeWidth={2} name="Time (s)" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Speedup and Efficiency Chart */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Speedup & Efficiency</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="speedup" fill="#10b981" name="Speedup (x)" />
                  <Bar dataKey="efficiency" fill="#f59e0b" name="Efficiency (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Throughput Chart */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Throughput</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis label={{ value: 'Files/s', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="throughput" stroke="#8b5cf6" strokeWidth={2} name="Throughput" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
