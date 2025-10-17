import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Hybrid Computing Analyzer
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Analyze performance with Thread + ProcessPool or MPI parallelization
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Thread + Process Card */}
        <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow">
          <div className="text-4xl mb-4">⚡</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Thread + ProcessPool
          </h2>
          <p className="text-gray-600 mb-6">
            Run hybrid analysis using ThreadPoolExecutor for I/O operations and ProcessPoolExecutor for CPU-bound tasks.
          </p>
          <ul className="text-sm text-gray-600 space-y-2 mb-6">
            <li>✓ Configure I/O threads (1-16)</li>
            <li>✓ Configure CPU processes (1-16)</li>
            <li>✓ Analyze up to 810 files</li>
            <li>✓ View detailed statistics</li>
          </ul>
          <Link
            href="/thread-process"
            className="block w-full bg-blue-600 text-white text-center py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Start Analysis →
          </Link>
        </div>

        {/* MPI Card */}
        <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow">
          <div className="text-4xl mb-4">🌐</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            MPI + ProcessPool
          </h2>
          <p className="text-gray-600 mb-6">
            Distribute workload across multiple MPI ranks for true distributed computing with hybrid parallelization.
          </p>
          <ul className="text-sm text-gray-600 space-y-2 mb-6">
            <li>✓ Configure MPI ranks (1-16)</li>
            <li>✓ Configure threads & processes per rank</li>
            <li>✓ Distributed file processing</li>
            <li>✓ Scalable architecture</li>
          </ul>
          <Link
            href="/mpi"
            className="block w-full bg-green-600 text-white text-center py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold"
          >
            Start MPI Analysis →
          </Link>
        </div>
      </div>

      {/* Info Section */}
      <div className="bg-white rounded-xl shadow-lg p-8 mt-8">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📊 Performance Tools</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Analysis</h4>
            <p className="text-sm text-gray-600 mb-3">Run individual analyses with custom configurations for Thread+Process or MPI modes.</p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Comparison</h4>
            <p className="text-sm text-gray-600 mb-3">Automated benchmarking with visual charts comparing different configurations.</p>
            <Link
              href="/comparison"
              className="inline-block bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm font-semibold"
            >
              View Comparisons →
            </Link>
          </div>
        </div>
      </div>

      {/* Info Section */}
      <div className="bg-white rounded-xl shadow-lg p-8 mt-8">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📊 About This Tool</h3>
        <div className="grid md:grid-cols-3 gap-6 text-sm text-gray-600">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Dataset</h4>
            <p>810 text files for comprehensive parallel computing analysis</p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Metrics</h4>
            <p>Speedup, throughput, efficiency, and detailed statistics</p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Technology</h4>
            <p>Python (FastAPI) + Next.js + Tailwind CSS</p>
          </div>
        </div>
      </div>

      {/* Student Info */}
      <div className="text-center text-gray-600 mt-8">
        <p className="font-semibold">Farid Firdaus - NPM: 237006081 - Kelas C</p>
        <p className="text-sm">UTS Komputasi Paralel 2025</p>
      </div>
    </div>
  );
}
